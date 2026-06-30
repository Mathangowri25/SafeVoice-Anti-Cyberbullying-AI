import os
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
MODEL_DIR   = os.path.join(PROJECT_DIR, "models", "safevoice_muril")

# ── Device & model ────────────────────────────────────────────────────────────
device    = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model     = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
model.to(device)
model.eval()

label_names = ["safe", "mild_toxic", "hate_speech", "severe"]

# ── Predict ───────────────────────────────────────────────────────────────────
def predict(text: str) -> dict:
    enc  = tokenizer(
        text,
        max_length     = 128,
        padding        = "max_length",
        truncation     = True,
        return_tensors = "pt",
    )
    ids  = enc["input_ids"].to(device)
    mask = enc["attention_mask"].to(device)

    with torch.no_grad():
        outputs = model(ids, attention_mask=mask)
        probs   = F.softmax(outputs.logits, dim=1).squeeze(0)  # shape: (4,)
        pred_id = torch.argmax(probs).item()

    return {
        "text":       text,
        "label":      label_names[pred_id],
        "severity":   pred_id,
        "confidence": round(probs[pred_id].item() * 100, 2),
        "scores": {
            label_names[i]: round(probs[i].item() * 100, 2)
            for i in range(len(label_names))
        },
    }

# ── Test texts ────────────────────────────────────────────────────────────────
test_texts = [
    "நீங்கள் எப்படி இருக்கீங்க?",       # Tamil: How are you? → safe
    "dei stupid fellow",                   # Tanglish mild insult
    "வெளியே போடா உன்னால முடியாது",        # Tamil insult
    "I will find you and hurt you",        # severe threat
]

# ── Output ────────────────────────────────────────────────────────────────────
print("=" * 55)
print("SAFEVOICE PREDICTION TEST")
print("=" * 55)

for text in test_texts:
    result = predict(text)
    print(f"\nText      : {result['text']}")
    print(f"Label     : {result['label'].upper()}")
    print(f"Severity  : {result['severity']}/3")
    print(f"Confidence: {result['confidence']}%")
    print(f"Scores    : { {k: f'{v}%' for k, v in result['scores'].items()} }")
