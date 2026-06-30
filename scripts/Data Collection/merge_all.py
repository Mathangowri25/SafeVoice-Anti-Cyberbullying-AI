"""
merge_all.py
Merges all scraped data from YouTube, Instagram, WhatsApp, and Telegram
into a single CSV for model training.

Place this file in: safevoice_dataset/scripts/
Output goes to:     safevoice_dataset/data/processed/merged_dataset.csv

File formats detected from your actual scraped files:
  YouTube   → *_youtube_comments.csv      | text col : "text"
  WhatsApp  → *_whatsapp_messages.csv     | text col : "text"
  Telegram  → *_telegram_scraped.xlsx     | sheet    : "Text Messages" | text col : "Text"
  Instagram → *_instagram_comments.xlsx   | sheet    : "Comments Data" | text col : "Comment Text"
"""

import os
import glob
import pandas as pd
from datetime import datetime

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))     # .../scripts/
DATASET_DIR   = os.path.abspath(os.path.join(BASE_DIR, "..")) # .../safevoice_dataset/
RAW_DIR       = os.path.join(DATASET_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(DATASET_DIR, "data", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)

# ── Source config ─────────────────────────────────────────────────────────────
# Format: "source_name": (glob_pattern, file_type, sheet_name_or_None, text_column)
SOURCES = {
    "youtube": (
        os.path.join(RAW_DIR, "youtube",   "*_youtube_comments.csv"),
        "csv",
        None,
        "text",
    ),
    "whatsapp": (
        os.path.join(RAW_DIR, "whatsapp",  "*_whatsapp_messages.csv"),
        "csv",
        None,
        "text",
    ),
    "telegram": (
        os.path.join(RAW_DIR, "telegram",  "*_telegram_scraped.xlsx"),
        "xlsx",
        "Text Messages",   # sheet name
        "Text",            # text column inside that sheet
    ),
    "instagram": (
        os.path.join(RAW_DIR, "instagram", "*_instagram_comments.xlsx"),
        "xlsx",
        "Comments Data",   # sheet name
        "Comment Text",    # text column inside that sheet
    ),
}

# ── Load & merge ──────────────────────────────────────────────────────────────
dfs = []

for source, (pattern, filetype, sheet_name, text_col) in SOURCES.items():
    matched_files = sorted(glob.glob(pattern))  # sorted = most-recent last

    if not matched_files:
        print(f"⚠️  No files found for [{source}]:\n   {pattern}")
        continue

    for filepath in matched_files:
        try:
            # ── Read file ────────────────────────────────────────────────────
            if filetype == "csv":
                df = pd.read_csv(filepath, encoding="utf-8-sig")

            elif filetype == "xlsx":
                xl       = pd.ExcelFile(filepath)
                # Use configured sheet; fall back to first sheet if missing
                sheet    = sheet_name if sheet_name in xl.sheet_names else xl.sheet_names[0]
                df       = pd.read_excel(filepath, sheet_name=sheet)

            # ── Validate text column exists ───────────────────────────────────
            if text_col not in df.columns:
                print(f"❌  Column '{text_col}' not found in {os.path.basename(filepath)}")
                print(f"    Available columns: {df.columns.tolist()}")
                continue

            # ── Normalize to unified schema ───────────────────────────────────
            out = pd.DataFrame()
            out["text"]     = df[text_col].astype(str)
            out["source"]   = source

            # Carry over label/severity if present (any casing)
            col_map = {c.lower(): c for c in df.columns}
            out["label"]    = df[col_map["label"]].astype(str)    if "label"    in col_map else ""
            out["severity"] = df[col_map["severity"]].astype(str) if "severity" in col_map else ""

            # ── Clean ─────────────────────────────────────────────────────────
            out.dropna(subset=["text"], inplace=True)
            out = out[out["text"].str.strip().str.lower() != "nan"]
            out = out[out["text"].str.strip() != ""]

            dfs.append(out)
            print(f"✅ Loaded {len(out):>5} rows  ← {os.path.basename(filepath)}")

        except Exception as e:
            print(f"❌ Error reading {os.path.basename(filepath)}: {e}")

# ── Validate ──────────────────────────────────────────────────────────────────
if not dfs:
    print("\n❌ No data loaded. Run the individual scrapers first:")
    print("   python scrape_youtube.py")
    print("   python scrape_instagram.py")
    print("   python parse_whatsapp.py")
    print("   python scrape_telegram.py")
    raise SystemExit(1)

# ── Concat & clean ────────────────────────────────────────────────────────────
merged = pd.concat(dfs, ignore_index=True)
merged.drop_duplicates(subset=["text"], inplace=True)
merged = merged[merged["text"].str.strip() != ""]
merged.reset_index(drop=True, inplace=True)

# ── Save ──────────────────────────────────────────────────────────────────────
timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = os.path.join(PROCESSED_DIR, f"{timestamp}_merged_dataset.csv")
merged.to_csv(output_path, index=False, encoding="utf-8-sig")

# ── Summary ───────────────────────────────────────────────────────────────────
print(f"\n{'─'*52}")
print(f"✅ Merged dataset saved to:")
print(f"   {output_path}")
print(f"   Total rows : {len(merged)}")
print(f"   Columns    : {merged.columns.tolist()}")
print(f"\n   Rows per source:")
for src, count in merged["source"].value_counts().items():
    print(f"     {src:<12}: {count}")
print(f"{'─'*52}")