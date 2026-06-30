# scripts/diagnose.py
import os
import sys
import pandas as pd
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
DATA_PATH   = os.path.join(PROJECT_DIR, "data", "labeled", "labeled_dataset.csv")
MODEL_PATH  = os.path.join(PROJECT_DIR, "models", "safevoice_muril")

LABEL_NAMES = ["safe", "mild_toxic", "hate_speech", "severe"]

# ═══════════════════════════════════════════════════════════════════════════════
# 1. DATASET CHECK
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 56)
print("1. DATASET CHECK")
print("=" * 56)

try:
    df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
    print(f"Path       : {DATA_PATH}")
    print(f"Total rows : {len(df)}")
    print(f"\nLabel distribution:")
    counts = df["label"].value_counts()
    pcts   = (counts / len(df) * 100).round(1)
    for label in LABEL_NAMES:
        count = counts.get(label, 0)
        pct   = pcts.get(label, 0.0)
        bar   = "█" * int(pct / 2)
        print(f"  {label:<14}: {count:>5} rows  ({pct:>5.1f}%)  {bar}")

    if "language" in df.columns:
        print(f"\nLanguage distribution:")
        for lang, cnt in df["language"].value_counts().items():
            print(f"  {lang:<12}: {cnt:>5} rows")

    # Warn if any label is severely underrepresented
    min_pct = pcts.min()
    if min_pct < 10:
        print(f"\nWARNING: '{pcts.idxmin()}' has only {min_pct}% of data.")
        print("         Consider adding more seed samples for that class.")

except FileNotFoundError:
    print(f"ERROR: Dataset not found at:\n  {DATA_PATH}")
    print("Run build_seed_dataset.py first.")
    sys.exit(1)
except Exception as e:
    print(f"Dataset error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# 2. MODEL CONFIG CHECK
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 56)
print("2. MODEL CONFIG CHECK")
print("=" * 56)

if not os.path.isdir(MODEL_PATH):
    print(f"ERROR: Model not found at:\n  {MODEL_PATH}")
    print("Run retrain_full.py first.")
    sys.exit(1)

try:
    model_check = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
    print(f"Path       : {MODEL_PATH}")
    print(f"num_labels : {model_check.config.num_labels}")
    print(f"id2label   : {model_check.config.id2label}")
    print(f"label2id   : {model_check.config.label2id}")

    # Warn if label map is wrong
    if model_check.config.num_labels != 4:
        print(f"\nWARNING: Expected 4 labels, got {model_check.config.num_labels}.")
        print("         Retrain with all 4 classes present in the dataset.")

    del model_check  # free memory before loading again below

except Exception as e:
    print(f"Model config error: {e}")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════════════════════
# 3. LIVE PREDICTION CHECK
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 56)
print("3. LIVE PREDICTION CHECK")
print("=" * 56)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device     : {device}\n")

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model     = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
model.to(device)
model.eval()

# Format: (text, expected_label, language_tag)
tests = [
    # Safe
    ("நீங்கள் எப்படி இருக்கீங்க?",                   "safe",        "Tamil"),
    ("How are you doing today?",                       "safe",        "English"),
    ("neenga epdi irukeenga bro",                      "safe",        "Tanglish"),
    ("aap kaise hain sab theek hai",                   "safe",        "Hindi"),

    # Mild toxic
    ("dei stupid fool get out of here",                "mild_toxic",  "English"),
    ("உனக்கு ஒன்றும் தெரியாது போடா",                  "mild_toxic",  "Tamil"),
    ("unakku onnum theriyaadu po da",                  "mild_toxic",  "Tanglish"),
    ("तुम बेकार हो चुप रहो",                           "mild_toxic",  "Hindi"),

    # Hate speech
    ("you and your kind don't belong here",            "hate_speech", "English"),
    ("உன் வகையினர் இங்கு வேண்டாம்",                   "hate_speech", "Tamil"),
    ("un jaathi aalunga ellam ippadi thaan",           "hate_speech", "Tanglish"),
    ("तुम्हारी जाति के लोग सब एक जैसे होते हैं",       "hate_speech", "Hindi"),

    # Severe
    ("I will find you and kill you tonight",           "severe",      "English"),
    ("உன்னை பாத்துக்கிறேன் நாளைக்கு விட மாட்டேன்",    "severe",      "Tamil"),
    ("unnai theditu varuven viduva maaten da",         "severe",      "Tanglish"),
    ("जान से मार दूंगा समझे कल तक का समय है",          "severe",      "Hindi"),
]

passed = 0
failures = []

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
        pred  = model.config.id2label[int(torch.argmax(probs).item())]

    ok     = pred == expected
    status = "PASS" if ok else "FAIL"
    if ok:
        passed += 1
    else:
        failures.append((lang, expected, pred, text))

    print(f"[{status}] {lang:<10} | expected: {expected:<14} got: {pred:<14} "
          f"conf: {probs.max()*100:.1f}%")
    print(f"       {text[:55]}")

    # Probability bars for all classes
    for i, name in enumerate(LABEL_NAMES):
        bar  = "█" * int(probs[i] * 20)
        mark = " <-- predicted" if i == int(torch.argmax(probs).item()) else ""
        print(f"       {name:<15}: {probs[i]*100:5.1f}%  {bar}{mark}")
    print()

# ═══════════════════════════════════════════════════════════════════════════════
# 4. SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 56)
print("4. SUMMARY")
print("=" * 56)
print(f"Predictions : {passed}/{len(tests)} correct")

if failures:
    print(f"\nFailed ({len(failures)}):")
    for lang, exp, got, text in failures:
        print(f"  [{lang}] expected '{exp}' → got '{got}'")
        print(f"          {text[:55]}")

print()
if passed == len(tests):
    print("All checks passed — model is healthy!")
    print("Restart your backend to use the latest model.")
elif passed >= len(tests) * 0.75:
    print("Model is mostly working but needs improvement.")
    print("Add more examples for the failing classes in build_seed_dataset.py")
    print("then re-run retrain_full.py.")
else:
    print("Model needs retraining — too many wrong predictions.")
    print("Steps to fix:")
    print("  1. Run build_seed_dataset.py to rebuild labeled_dataset.csv")
    print("  2. Check label balance above (each class should be > 10%)")
    print("  3. Run retrain_full.py with EPOCHS=6 or higher")
    print("  4. Re-run this script to verify")

sys.exit(0 if passed == len(tests) else 1)