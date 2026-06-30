# scripts/model_inference.py
import os
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
MODEL_PATH  = os.path.join(PROJECT_DIR, "models", "safevoice_muril")

# ── Config ────────────────────────────────────────────────────────────────────
MAX_LEN = 128

LABEL_SEVERITY = {
    "safe":        0,
    "mild_toxic":  1,
    "hate_speech": 2,
    "severe":      3,
}

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ── Lazy-loaded singletons ────────────────────────────────────────────────────
_tokenizer = None
_model     = None


def load_model():
    global _tokenizer, _model
    if _model is None:
        if not os.path.isdir(MODEL_PATH):
            raise FileNotFoundError(
                f"Model not found at:\n  {MODEL_PATH}\n"
                "Run retrain_full.py first to train and save the model."
            )
        print(f"Loading SafeVoice model from:\n  {MODEL_PATH}")
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        _model     = AutoModelForSequenceClassification.from_pretrained(
                        MODEL_PATH)
        _model.to(device)
        _model.eval()
        print(f"Model ready on {device} | Labels: {_model.config.id2label}")
    return _model, _tokenizer


def predict_text(text: str) -> dict:
    """
    Run inference on a single text string.

    Returns:
        {
            "label":      str,   # e.g. "hate_speech"
            "severity":   int,   # 0–3
            "confidence": float, # top-class probability as percentage
            "scores":     dict,  # {label_name: probability_%} for all classes
        }
    """
    mdl, tok = load_model()

    enc  = tok(
        str(text),
        max_length=MAX_LEN,
        padding="max_length",
        truncation=True,
        return_tensors="pt"
    )
    ids  = enc["input_ids"].to(device)
    mask = enc["attention_mask"].to(device)

    with torch.no_grad():
        out     = mdl(ids, attention_mask=mask)
        probs   = F.softmax(out.logits, dim=1).squeeze()
        pred_id = int(torch.argmax(probs).item())

    id2label        = mdl.config.id2label
    predicted_label = id2label.get(pred_id, "safe")
    severity        = LABEL_SEVERITY.get(predicted_label, 0)

    scores = {
        id2label.get(i, f"label_{i}"): round(float(probs[i]) * 100, 2)
        for i in range(len(id2label))
    }

    return {
        "label":      predicted_label,
        "severity":   severity,
        "confidence": round(float(probs[pred_id]) * 100, 2),
        "scores":     scores,
    }


# ── Quick smoke-test when run directly ───────────────────────────────────────
if __name__ == "__main__":
    test_cases = [
        ("நீங்கள் எப்படி இருக்கீங்க?",          "Tamil  · safe"),
        ("dei muttaal fellow shut up",             "Tanglish · mild"),
        ("you and your kind don't belong here",    "English · hate"),
        ("I will find you and hurt you badly",     "English · severe"),
        ("तुम बेकार हो यहाँ से चले जाओ",          "Hindi  · hate"),
        ("unna viduva maaten unnai theditu varuven","Tanglish · severe"),
    ]

    print(f"\n{'─' * 60}")
    print("SafeVoice inference smoke-test")
    print(f"{'─' * 60}\n")

    for text, expected in test_cases:
        result = predict_text(text)
        print(f"Input    : {text}")
        print(f"Expected : {expected}")
        print(f"Got      : {result['label']} (severity={result['severity']}, "
              f"confidence={result['confidence']}%)")
        print(f"Scores   : { {k: f'{v}%' for k, v in result['scores'].items()} }")
        print()