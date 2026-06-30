import os
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.metrics import classification_report, confusion_matrix

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
TEST_PATH   = os.path.join(PROJECT_DIR, "data", "processed", "test.csv")
MODEL_DIR   = os.path.join(PROJECT_DIR, "models", "safevoice_muril")

# ── Device & model ────────────────────────────────────────────────────────────
device    = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model     = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
model.to(device)
model.eval()

# Full label map — id → name
LABEL_MAP = {
    0: "safe",
    1: "mild_toxic",
    2: "hate_speech",
    3: "severe",
}

# ── Dataset ───────────────────────────────────────────────────────────────────
class TestDataset(Dataset):
    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path, encoding="utf-8-sig")
        if "label_id" not in self.df.columns:
            raise ValueError(
                f"'label_id' column missing in {csv_path}.\n"
                "Re-run the split script to regenerate train/val/test CSVs."
            )
        self.df = self.df.dropna(subset=["text", "label_id"]).reset_index(drop=True)

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        text  = str(self.df.iloc[idx]["text"])
        label = int(self.df.iloc[idx]["label_id"])
        enc   = tokenizer(
            text,
            max_length     = 128,
            padding        = "max_length",
            truncation     = True,
            return_tensors = "pt",
        )
        return {
            "input_ids":      enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "label":          torch.tensor(label, dtype=torch.long),
        }

# ── Inference ─────────────────────────────────────────────────────────────────
loader = DataLoader(TestDataset(TEST_PATH), batch_size=32)

all_preds, all_labels = [], []
with torch.no_grad():
    for batch in loader:
        ids    = batch["input_ids"].to(device)
        mask   = batch["attention_mask"].to(device)
        labels = batch["label"].to(device)

        outputs = model(ids, attention_mask=mask)
        preds   = torch.argmax(outputs.logits, dim=1)

        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

# ── Fix: detect only the classes actually present in this test set ────────────
present_ids   = sorted(set(all_labels) | set(all_preds))   # union of true + predicted
present_names = [LABEL_MAP[i] for i in present_ids]

missing = [LABEL_MAP[i] for i in LABEL_MAP if i not in present_ids]
if missing:
    print(f"⚠️  Classes absent from test set: {missing}")
    print(f"   These need more labeled examples in your dataset.\n")

# ── Results ───────────────────────────────────────────────────────────────────
print("=" * 50)
print("SAFEVOICE MODEL EVALUATION RESULTS")
print("=" * 50)

print(classification_report(
    all_labels,
    all_preds,
    labels        = present_ids,    # only score classes that exist
    target_names  = present_names,  # matching names for those classes
    zero_division = 0,
))

# ── Confusion matrix ──────────────────────────────────────────────────────────
cm = confusion_matrix(all_labels, all_preds, labels=present_ids)
print("Confusion Matrix:")
print(pd.DataFrame(cm, index=present_names, columns=present_names))
