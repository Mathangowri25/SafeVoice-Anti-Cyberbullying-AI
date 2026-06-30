import os
import pandas as pd
import torch
from torch.utils.data import Dataset
from transformers import AutoTokenizer

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
TRAIN_PATH  = os.path.join(PROJECT_DIR, "data", "processed", "train.csv")
VAL_PATH    = os.path.join(PROJECT_DIR, "data", "processed", "val.csv")
TEST_PATH   = os.path.join(PROJECT_DIR, "data", "processed", "test.csv")

# ── Model ─────────────────────────────────────────────────────────────────────
MODEL_NAME = "google/muril-base-cased"   # multilingual model for Indian languages
tokenizer  = AutoTokenizer.from_pretrained(MODEL_NAME)


# ── Dataset class ─────────────────────────────────────────────────────────────
class ToxicityDataset(Dataset):
    def __init__(self, csv_path, tokenizer, max_len=128):
        self.df        = pd.read_csv(csv_path, encoding="utf-8-sig")
        self.tokenizer = tokenizer
        self.max_len   = max_len

        # Guard: label_id must exist (created by the split script)
        if "label_id" not in self.df.columns:
            raise ValueError(
                f"'label_id' column not found in {csv_path}.\n"
                "Re-run the split script (step7) to regenerate train/val/test CSVs."
            )

        # Drop any rows where text or label_id is missing
        self.df = self.df.dropna(subset=["text", "label_id"]).reset_index(drop=True)

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        text  = str(self.df.iloc[idx]["text"])
        label = int(self.df.iloc[idx]["label_id"])

        encoding = self.tokenizer(
            text,
            max_length     = self.max_len,
            padding        = "max_length",
            truncation     = True,
            return_tensors = "pt",
        )

        return {
            "input_ids":      encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "label":          torch.tensor(label, dtype=torch.long),
        }


# ── Test ──────────────────────────────────────────────────────────────────────
train_dataset = ToxicityDataset(TRAIN_PATH, tokenizer)
val_dataset   = ToxicityDataset(VAL_PATH,   tokenizer)
test_dataset  = ToxicityDataset(TEST_PATH,  tokenizer)

sample = train_dataset[0]
print("input_ids shape :", sample["input_ids"].shape)
print("attention_mask  :", sample["attention_mask"].shape)
print("label           :", sample["label"])
print()
print(f"Train samples : {len(train_dataset)}")
print(f"Val   samples : {len(val_dataset)}")
print(f"Test  samples : {len(test_dataset)}")
print()
print("✅ Dataset ready!")
