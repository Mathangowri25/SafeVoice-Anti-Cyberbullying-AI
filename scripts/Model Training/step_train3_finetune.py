import os
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    get_linear_schedule_with_warmup,
)
from torch.optim import AdamW

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
TRAIN_PATH  = os.path.join(PROJECT_DIR, "data", "processed", "train.csv")
VAL_PATH    = os.path.join(PROJECT_DIR, "data", "processed", "val.csv")
MODEL_OUT   = os.path.join(PROJECT_DIR, "models", "safevoice_muril")
os.makedirs(MODEL_OUT, exist_ok=True)

# ── Config ────────────────────────────────────────────────────────────────────
MODEL_NAME    = "google/muril-base-cased"
NUM_LABELS    = 4          # safe, mild_toxic, hate_speech, severe
EPOCHS        = 4
BATCH_SIZE    = 16
MAX_LEN       = 128
LEARNING_RATE = 2e-5

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# ── Tokenizer & model ─────────────────────────────────────────────────────────
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model     = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME, num_labels=NUM_LABELS
)
model.to(device)

# ── Dataset ───────────────────────────────────────────────────────────────────
class ToxicityDataset(Dataset):
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
            max_length     = MAX_LEN,
            padding        = "max_length",
            truncation     = True,
            return_tensors = "pt",
        )
        return {
            "input_ids":      enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "label":          torch.tensor(label, dtype=torch.long),
        }

# ── DataLoaders ───────────────────────────────────────────────────────────────
train_loader = DataLoader(ToxicityDataset(TRAIN_PATH),
                          batch_size=BATCH_SIZE, shuffle=True)
val_loader   = DataLoader(ToxicityDataset(VAL_PATH),
                          batch_size=BATCH_SIZE)

# ── Optimizer & scheduler ─────────────────────────────────────────────────────
optimizer   = AdamW(model.parameters(), lr=LEARNING_RATE)
total_steps = len(train_loader) * EPOCHS
scheduler   = get_linear_schedule_with_warmup(
    optimizer,
    num_warmup_steps   = total_steps // 10,
    num_training_steps = total_steps,
)

# ── Evaluation ────────────────────────────────────────────────────────────────
def evaluate(loader):
    model.eval()
    correct, total, total_loss = 0, 0, 0.0
    with torch.no_grad():
        for batch in loader:
            ids    = batch["input_ids"].to(device)
            mask   = batch["attention_mask"].to(device)
            labels = batch["label"].to(device)

            outputs = model(ids, attention_mask=mask, labels=labels)
            preds   = torch.argmax(outputs.logits, dim=1)

            correct    += (preds == labels).sum().item()
            total      += labels.size(0)
            total_loss += outputs.loss.item()

    return correct / total, total_loss / len(loader)

# ── Training loop ─────────────────────────────────────────────────────────────
print("\nStarting training...")
for epoch in range(EPOCHS):
    model.train()
    running_loss = 0.0

    for step, batch in enumerate(train_loader):
        ids    = batch["input_ids"].to(device)
        mask   = batch["attention_mask"].to(device)
        labels = batch["label"].to(device)

        optimizer.zero_grad()
        outputs = model(ids, attention_mask=mask, labels=labels)
        loss    = outputs.loss
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()

        running_loss += loss.item()

        if step % 50 == 0:
            print(f"  Epoch {epoch+1} | Step {step}/{len(train_loader)}"
                  f" | Loss: {loss.item():.4f}")

    val_acc, val_loss = evaluate(val_loader)
    print(f"\nEpoch {epoch+1} done | "
          f"Val Accuracy: {val_acc:.4f} | Val Loss: {val_loss:.4f}\n")

# ── Save ──────────────────────────────────────────────────────────────────────
model.save_pretrained(MODEL_OUT)
tokenizer.save_pretrained(MODEL_OUT)
print(f"✅ Model saved to: {MODEL_OUT}")