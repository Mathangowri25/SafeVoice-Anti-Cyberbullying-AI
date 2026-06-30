"""
WhatsApp Chat Parser
Parses exported WhatsApp .txt files into structured CSV.

Usage:
    1. Export WhatsApp chat: Chat > More > Export Chat > Without Media
    2. Place the .txt file(s) in: data/raw/whatsapp/
    3. Run: python scrape_whatsapp.py
"""

import os                          # ✅ FIX 1: was missing
import re
import glob
from datetime import datetime      # ✅ FIX 2: was missing
import pandas as pd

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "raw", "whatsapp"))

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)


def parse_whatsapp_chat(filepath):
    """
    Parses exported WhatsApp .txt file into structured rows.
    Handles both 12hr and 24hr time formats.
    """
    pattern = re.compile(
        r'(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}(?:\s?[APap][Mm])?)\s-\s([^:]+):\s(.+)'
    )

    messages = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            match = pattern.match(line.strip())
            if match:
                date, time_str, sender, text = match.groups()
                # Skip system messages
                if "Messages and calls are end-to-end" in text:
                    continue
                if "added" in text or "removed" in text:
                    continue
                messages.append({
                    "text":      text,
                    "platform":  "whatsapp",
                    "sender":    sender,
                    "date":      date,
                    "time":      time_str,
                    "label":     "",
                    "severity":  ""
                })
    return pd.DataFrame(messages)


# ── Process all exported .txt files ─────────────────────────────────────────
txt_files = glob.glob(os.path.join(OUTPUT_DIR, "*.txt"))

if not txt_files:
    raise FileNotFoundError(
        f"No .txt files found in:\n{OUTPUT_DIR}\n"
        "Export a WhatsApp chat and place the .txt file there."
    )

all_dfs = []
for filepath in txt_files:
    print(f"Parsing: {filepath}")
    df = parse_whatsapp_chat(filepath)
    print(f"  → {len(df)} messages found")
    all_dfs.append(df)

# ✅ FIX 3: was pd.DataFrame(all_comments) — wrong variable, should concat all_dfs
df = pd.concat(all_dfs, ignore_index=True)

# ── Clean ────────────────────────────────────────────────────────────────────
df.drop_duplicates(subset=["text"], inplace=True)
df = df[df["text"].str.strip() != ""]

# ── Save ─────────────────────────────────────────────────────────────────────
# ✅ FIX 4: was _youtube_comments.csv — renamed to _whatsapp_messages.csv
filename    = datetime.now().strftime("%Y%m%d_%H%M%S") + "_whatsapp_messages.csv"
output_path = os.path.join(OUTPUT_DIR, filename)

df.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"\n✅ Saved {len(df)} messages to:\n{output_path}")