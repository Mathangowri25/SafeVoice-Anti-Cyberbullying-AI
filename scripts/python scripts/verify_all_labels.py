# scripts/verify_all_labels.py
import os
import sys
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
MODEL_PATH  = os.path.join(PROJECT_DIR, "models", "safevoice_muril")

# ── Load model ────────────────────────────────────────────────────────────────
if not os.path.isdir(MODEL_PATH):
    print(f"ERROR: Model not found at:\n  {MODEL_PATH}")
    print("Run retrain_full.py first to train and save the model.")
    sys.exit(1)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device : {device}")
print(f"Loading model from:\n  {MODEL_PATH}\n")

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model     = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
model.to(device)
model.eval()

ID2LABEL = model.config.id2label
print("Model label map:", ID2LABEL)

# ── Test cases ────────────────────────────────────────────────────────────────
# Format: (text, expected_label, language_tag)
tests = [
    # Safe
    ("நீங்கள் எப்படி இருக்கீங்க?",                   "safe",        "Tamil"),
    ("How are you doing today?",                       "safe",        "English"),
    ("aap kaise hain?",                                "safe",        "Hindi"),
    ("neenga epdi irukeenga bro?",                     "safe",        "Tanglish"),

    # Mild toxic
    ("dei stupid fool shut up",                        "mild_toxic",  "English"),
    ("உனக்கு ஒன்றும் தெரியாது போடா",                  "mild_toxic",  "Tamil"),
    ("तुम बेकार हो चुप रहो",                           "mild_toxic",  "Hindi"),
    ("unakku onnum theriyaadu po da",                  "mild_toxic",  "Tanglish"),

    # Hate speech
    ("you and your kind don't belong here",            "hate_speech", "English"),
    ("உன் வகையினர் இங்கு வேண்டாம்",                   "hate_speech", "Tamil"),
    ("तुम्हारी जाति के लोग सब एक जैसे होते हैं",       "hate_speech", "Hindi"),
    ("un jaathi aalunga ellam ippadi thaan iruppanga", "hate_speech", "Tanglish"),

    # Severe
    ("I will find you and kill you tonight",           "severe",      "English"),
    ("உன்னை பாத்துக்கிறேன் நாளைக்கு விட மாட்டேன்",    "severe",      "Tamil"),
    ("जान से मार दूंगा समझे कल तक का समय है",          "severe",      "Hindi"),
    ("unnai theditu varuven viduva maaten da",         "severe",      "Tanglish"),
]

# ── Run verification ──────────────────────────────────────────────────────────
passed = 0
failures = []

print("\n" + "=" * 68)
print(f"{'STATUS':<8} {'LANG':<10} {'EXPECTED':<14} {'GOT':<14} {'CONF':>6}  TEXT")
print("=" * 68)

for text, expected, lang in tests:
    enc = tokenizer(
        text,
        max_length=128,
        padding="max_length",
        truncation=True,
        return_tensors="pt"
    )
    with torch.no_grad():
        out   = model(
            enc["input_ids"].to(device),
            attention_mask=enc["attention_mask"].to(device)
        )
        probs = F.softmax(out.logits, dim=1).squeeze()
        pred  = ID2LABEL[int(torch.argmax(probs).item())]

    ok     = pred == expected
    status = "PASS" if ok else "FAIL"
    conf   = f"{probs.max() * 100:.1f}%"

    if ok:
        passed += 1
    else:
        failures.append((lang, expected, pred, text))

    print(f"{status:<8} {lang:<10} {expected:<14} {pred:<14} {conf:>6}  "
          f"{text[:38]}")

# ── Summary ───────────────────────────────────────────────────────────────────
print("=" * 68)
print(f"\nResult: {passed}/{len(tests)} passed")

if failures:
    print(f"\nFailed cases ({len(failures)}):")
    for lang, exp, got, text in failures:
        print(f"  [{lang}] expected '{exp}' → got '{got}' | {text[:50]}")

print()
if passed == len(tests):
    print("All tests passed — model is working correctly!")
    print("Restart your backend to pick up the latest model.")
elif passed >= len(tests) * 0.75:
    print("Most tests passed — model is working but may need more training.")
    print("Check the failed cases above and add them to your seed dataset.")
else:
    print("Too many failures — run retrain_full.py with more labeled data.")
    print("Check class weights and make sure all 4 labels are in training set.")

sys.exit(0 if passed == len(tests) else 1)