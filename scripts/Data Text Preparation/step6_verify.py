import os
import pandas as pd

# ── Path fix ──────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))   # .../scripts/Data Text Preparation/
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))  # .../safevoice_Project/
INPUT_PATH  = os.path.join(PROJECT_DIR, "data", "labeled", "auto_labeled.csv")

df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig")

print("=" * 40)
print("SAFEVOICE DATASET SUMMARY")
print("=" * 40)
print(f"Total rows        : {len(df)}")

print(f"\nPlatform split:")
print(df["source"].value_counts())

print(f"\nLanguage split:")
print(df["language"].value_counts())

print(f"\nLabel distribution:")
print(df["label"].value_counts())

print(f"\nSeverity distribution:")
print(df["severity"].value_counts())

print(f"\nSample rows:")
print(df[["text", "language", "source", "label", "severity"]].sample(5))

# ── Readiness check ───────────────────────────────────────────────────────────
labeled_count = df[df["label"].notna() & (df["label"].str.strip() != "")].shape[0]
print(f"\nLabeled rows: {labeled_count} / {len(df)}")

if labeled_count >= 5000:
    print("✅ Dataset is ready for model training!")
else:
    needed = 5000 - labeled_count
    print(f"⚠️  Need {needed} more labeled rows before training.")