import os
import pandas as pd
import re
import emoji

# ── Path fix: resolve relative to this script's location ─────────────────────
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))          # .../scripts/
PROJECT_DIR   = os.path.abspath(os.path.join(BASE_DIR, ".."))       # .../safevoice_Project/
INPUT_PATH    = os.path.join(PROJECT_DIR, "data", "processed", "20260426_152127_merged_dataset.csv")
OUTPUT_PATH   = os.path.join(PROJECT_DIR, "data", "processed", "step1_cleaned.csv")

# ── Load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig")
print(f"Before cleaning: {len(df)} rows")

# 1. Drop rows with no text
df.dropna(subset=["text"], inplace=True)

# 2. Remove duplicates
df.drop_duplicates(subset=["text"], inplace=True)

# 3. Remove rows that are too short (less than 4 characters)
df = df[df["text"].str.strip().str.len() >= 4]

# 4. Remove WhatsApp system messages
system_phrases = [
    "Messages and calls are end-to-end encrypted",
    "added you", "removed you", "left", "changed the group",
    "changed this group", "You deleted this message",
    "<Media omitted>", "image omitted", "video omitted",
    "null", "This message was deleted"
]
for phrase in system_phrases:
    df = df[~df["text"].str.contains(phrase, case=False, na=False)]

# 5. Remove pure URLs
df = df[~df["text"].str.match(r'^\s*https?://\S+\s*$')]

# 6. Clean text — remove URLs, extra spaces
def clean_text(text):
    text = re.sub(r'http\S+|www\.\S+', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

df["text"] = df["text"].apply(clean_text)
df = df[df["text"].str.len() >= 4]   # re-check after cleaning

# ── Save ──────────────────────────────────────────────────────────────────────
df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
print(f"After cleaning: {len(df)} rows")
print(df["source"].value_counts())