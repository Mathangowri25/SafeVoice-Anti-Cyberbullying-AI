# scripts/retrain_full.py
import os
import pandas as pd
import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import get_linear_schedule_with_warmup
from torch.optim import AdamW
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
DATA_PATH   = os.path.join(PROJECT_DIR, "data", "labeled", "labeled_dataset.csv")
MODEL_DIR   = os.path.join(PROJECT_DIR, "models", "safevoice_muril")

os.makedirs(MODEL_DIR, exist_ok=True)

# ── Config ────────────────────────────────────────────────────────────────────
MODEL_NAME = "google/muril-base-cased"
NUM_LABELS = 4
EPOCHS     = 6
BATCH_SIZE = 8
MAX_LEN    = 128
LR         = 2e-5

LABEL_MAP = {"safe": 0, "mild_toxic": 1, "hate_speech": 2, "severe": 3}
ID2LABEL  = {0: "safe", 1: "mild_toxic", 2: "hate_speech", 3: "severe"}

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device: {device}")

# ── Load and prepare data ─────────────────────────────────────────────────────
df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
df = df[df["label"].isin(LABEL_MAP.keys())].copy()
df["label_id"] = df["label"].map(LABEL_MAP)
df = df[df["text"].notna() & (df["text"].str.len() > 3)]

print(f"\nDataset size: {len(df)}")
print(df["label"].value_counts())

train_df, temp_df = train_test_split(
    df, test_size=0.2, random_state=42, stratify=df["label_id"]
)
val_df, test_df = train_test_split(
    temp_df, test_size=0.5, random_state=42, stratify=temp_df["label_id"]
)

print(f"\nTrain: {len(train_df)} | Val: {len(val_df)} | Test: {len(test_df)}")

# ── Tokenizer ─────────────────────────────────────────────────────────────────
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

# ── Dataset class ─────────────────────────────────────────────────────────────
class ToxicSet(Dataset):
    def __init__(self, df):
        self.df = df.reset_index(drop=True)

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        text  = str(self.df.loc[idx, "text"])
        label = int(self.df.loc[idx, "label_id"])
        enc   = tokenizer(
            text,
            max_length=MAX_LEN,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        return {
            "input_ids":      enc["input_ids"].squeeze(),
            "attention_mask": enc["attention_mask"].squeeze(),
            "label":          torch.tensor(label, dtype=torch.long)
        }

train_loader = DataLoader(ToxicSet(train_df), batch_size=BATCH_SIZE, shuffle=True)
val_loader   = DataLoader(ToxicSet(val_df),   batch_size=BATCH_SIZE)
test_loader  = DataLoader(ToxicSet(test_df),  batch_size=BATCH_SIZE)

# ── Model ─────────────────────────────────────────────────────────────────────
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=NUM_LABELS,
    id2label=ID2LABEL,
    label2id=LABEL_MAP,
)
model.to(device)

# ── Weighted loss ─────────────────────────────────────────────────────────────
class_weights = compute_class_weight(
    "balanced",
    classes=np.array([0, 1, 2, 3]),
    y=train_df["label_id"].values
)
weights = torch.tensor(class_weights, dtype=torch.float).to(device)
print(f"\nClass weights: {class_weights.round(3)}")
loss_fn = torch.nn.CrossEntropyLoss(weight=weights)

# ── Optimizer and scheduler ───────────────────────────────────────────────────
optimizer   = AdamW(model.parameters(), lr=LR, weight_decay=0.01)
total_steps = len(train_loader) * EPOCHS
scheduler   = get_linear_schedule_with_warmup(
    optimizer,
    num_warmup_steps=total_steps // 10,
    num_training_steps=total_steps
)

# ── Eval function ─────────────────────────────────────────────────────────────
def evaluate(loader):
    model.eval()
    all_preds, all_labels = [], []
    total_loss = 0
    with torch.no_grad():
        for batch in loader:
            ids    = batch["input_ids"].to(device)
            mask   = batch["attention_mask"].to(device)
            labels = batch["label"].to(device)
            out    = model(ids, attention_mask=mask)
            loss   = loss_fn(out.logits, labels)
            preds  = torch.argmax(out.logits, dim=1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            total_loss += loss.item()
    acc = sum(p == l for p, l in zip(all_preds, all_labels)) / len(all_labels)
    return acc, total_loss / len(loader), all_preds, all_labels

# ── Training loop ─────────────────────────────────────────────────────────────
print("\nTraining started...\n")
best_acc = 0

for epoch in range(EPOCHS):
    model.train()
    total_loss = 0

    for step, batch in enumerate(train_loader):
        ids    = batch["input_ids"].to(device)
        mask   = batch["attention_mask"].to(device)
        labels = batch["label"].to(device)

        optimizer.zero_grad()
        out  = model(ids, attention_mask=mask)
        loss = loss_fn(out.logits, labels)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()
        total_loss += loss.item()

        if step % 20 == 0:
            print(f"  Epoch {epoch+1} | Step {step:3d}/{len(train_loader)} "
                  f"| Loss: {loss.item():.4f}")

    val_acc, val_loss, _, _ = evaluate(val_loader)
    avg_train_loss = total_loss / len(train_loader)
    print(f"\nEpoch {epoch+1} complete | "
          f"Train Loss: {avg_train_loss:.4f} | "
          f"Val Acc: {val_acc:.4f} | Val Loss: {val_loss:.4f}")

    if val_acc > best_acc:
        best_acc = val_acc
        model.save_pretrained(MODEL_DIR)
        tokenizer.save_pretrained(MODEL_DIR)
        print(f"  Saved best model → {MODEL_DIR} (acc={val_acc:.4f})\n")

# ── Final test evaluation ─────────────────────────────────────────────────────
print("\n" + "=" * 52)
print("FINAL TEST EVALUATION")
print("=" * 52)
_, _, preds, labels = evaluate(test_loader)
print(classification_report(
    labels, preds,
    target_names=["safe", "mild_toxic", "hate_speech", "severe"]
))
print(f"Best validation accuracy: {best_acc:.4f}")
print(f"Model saved to: {MODEL_DIR}")