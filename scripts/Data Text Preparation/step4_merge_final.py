import os
import pandas as pd

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
INPUT_PATH  = os.path.join(PROJECT_DIR, "data", "processed", "step3_preprocessed.csv")
OUTPUT_PATH = os.path.join(PROJECT_DIR, "data", "processed", "final_unlabeled.csv")

# ── Load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig")
print(f"Loaded {len(df)} rows")

# ── Add label/severity columns if not present ─────────────────────────────────
if "label" not in df.columns:
    df["label"] = ""
if "severity" not in df.columns:
    df["severity"] = ""

# ── Select only the columns needed for labeling ───────────────────────────────
# Each column is included only if it actually exists in the dataframe
desired_cols = ["text", "text_clean", "language", "source", "label", "severity"]
final_cols   = [c for c in desired_cols if c in df.columns]
df_final     = df[final_cols]

# ── Stats ─────────────────────────────────────────────────────────────────────
# merged_dataset uses "source" not "platform" — check both
source_col = "source" if "source" in df.columns else "platform" if "platform" in df.columns else None

if source_col:
    print(f"\nSource distribution ({source_col}):")
    print(df[source_col].value_counts())
else:
    print("\nNo source/platform column found")

print("\nLanguage distribution:")
print(df["language"].value_counts())

print(f"\nTotal rows ready for labeling: {len(df_final)}")
print(f"Columns: {final_cols}")

# ── Save ──────────────────────────────────────────────────────────────────────
df_final.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
print(f"\nSaved {len(df_final)} rows → {OUTPUT_PATH}")