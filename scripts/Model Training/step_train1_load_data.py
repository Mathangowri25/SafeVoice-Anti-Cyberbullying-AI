import os
import pandas as pd
from sklearn.model_selection import train_test_split

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
INPUT_PATH  = os.path.join(PROJECT_DIR, "data", "labeled", "auto_labeled.csv")
OUT_DIR     = os.path.join(PROJECT_DIR, "data", "processed")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig")

# ── Map labels ────────────────────────────────────────────────────────────────
label_map = {
    "safe":        0,
    "mild_toxic":  1,
    "hate_speech": 2,
    "severe":      3,
}
df = df[df["label"].isin(label_map.keys())]
df["label_id"] = df["label"].map(label_map)

print("Label distribution before split:")
print(df["label"].value_counts())
print()

# ── Fix: drop classes with fewer than 3 rows (can't split into train/val/test) 
class_counts = df["label_id"].value_counts()
valid_classes = class_counts[class_counts >= 3].index
dropped       = class_counts[class_counts < 3].index.tolist()

if dropped:
    dropped_names = [k for k, v in label_map.items() if v in dropped]
    print(f"⚠️  Dropping under-represented classes (< 3 rows): {dropped_names}")
    print(f"   Add more examples of these labels and re-run step5_autolabel.py")
    print()
    df = df[df["label_id"].isin(valid_classes)]

# ── Split: 80% train | 10% val | 10% test ────────────────────────────────────
# stratify only when every remaining class has >= 2 members in temp_df too
train_df, temp_df = train_test_split(
    df, test_size=0.2, random_state=42, stratify=df["label_id"]
)

# Check temp_df class counts before second split
temp_counts   = temp_df["label_id"].value_counts()
can_stratify2 = (temp_counts >= 2).all()

val_df, test_df = train_test_split(
    temp_df,
    test_size=0.5,
    random_state=42,
    stratify=temp_df["label_id"] if can_stratify2 else None,
)

# ── Save ──────────────────────────────────────────────────────────────────────
train_df.to_csv(os.path.join(OUT_DIR, "train.csv"), index=False, encoding="utf-8-sig")
val_df.to_csv(  os.path.join(OUT_DIR, "val.csv"),   index=False, encoding="utf-8-sig")
test_df.to_csv( os.path.join(OUT_DIR, "test.csv"),  index=False, encoding="utf-8-sig")

print("Label distribution after split:")
print(f"  Train : {len(train_df)} rows  {dict(train_df['label'].value_counts())}")
print(f"  Val   : {len(val_df)} rows   {dict(val_df['label'].value_counts())}")
print(f"  Test  : {len(test_df)} rows   {dict(test_df['label'].value_counts())}")
print(f"\n✅ Saved to: {OUT_DIR}")

# ── Readiness check ───────────────────────────────────────────────────────────
if len(train_df) < 5000:
    needed = 5000 - len(train_df)
    print(f"\n⚠️  Training set has {len(train_df)} rows.")
    print(f"   Collect {needed} more labeled rows for a stronger model.")
else:
    print(f"\n✅ Training set is large enough for model training.")
