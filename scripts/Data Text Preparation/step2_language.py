import os
import re
import pandas as pd
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

DetectorFactory.seed = 42

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
INPUT_PATH  = os.path.join(PROJECT_DIR, "data", "processed", "step1_cleaned.csv")
OUTPUT_PATH = os.path.join(PROJECT_DIR, "data", "processed", "step2_with_language.csv")

# ── Tanglish detector (Tamil words written in Roman/English script) ────────────
# These are extremely common Tamil words/suffixes that appear in Tanglish text.
# langdetect will wrongly label these as "en" or "so" — we catch them first.
TANGLISH_PATTERNS = [
    r'\b(enna|enna da|yenna|aama|illai|illa|sollu|solla|vandhaan|vanthu|ponga|pongo)\b',
    r'\b(nalla|romba|konjam|vera|level|nallavanga|machaan|macha|anna|akka|appa|amma)\b',
    r'\b(paaru|paaren|paaruda|theriyum|theriyala|therila|puriala|puriyala|puriyum)\b',
    r'\b(poi|poyitu|vandha|varuvaan|varuven|vaanga|vaanganum|vaangitten)\b',
    r'\b(kaasu|paise|yaar|yaaru|yaaruvum|yaarum|ellam|ellaru|avan|aval|avanga)\b',
    r'\b(seri|sari|otrai|ooru|oruthan|orutha|pannuvan|panrom|pannuvom|panniten)\b',
    r'\b(iruku|irukku|iruken|irukka|illa|illama|illena|vendam|vendum|venda)\b',
    r'\b(epdi|eppadi|eppo|eppov|evlo|evvlo|evvalavu|ingaye|inga|ange|anga|enga)\b',
    r'\b(kadhal|kadhalikiren|kadhala|love|fight|mokka|scene|mass|class|boss)\b',
    r'\b(da\b|di\b|bro|mapla|machan|dei|dey|aiyo|aiyoo|ayyo|adei|adeda)\b',
]

TANGLISH_REGEX = re.compile(
    '|'.join(TANGLISH_PATTERNS),
    flags=re.IGNORECASE
)

def is_tanglish(text: str) -> bool:
    """Returns True if the text looks like Tamil written in Roman script."""
    matches = TANGLISH_REGEX.findall(str(text))
    # If 2+ Tanglish markers found, treat as Tanglish
    return len(matches) >= 2


def detect_language(text: str) -> str:
    text = str(text).strip()

    # Check Tanglish BEFORE langdetect (langdetect cannot detect it)
    if is_tanglish(text):
        return "Tanglish"

    try:
        lang = detect(text)
        lang_map = {
            "ta": "Tamil",
            "hi": "Hindi",
            "en": "English",
            "ml": "Malayalam",
            "te": "Telugu",
        }
        return lang_map.get(lang, f"other:{lang}")
    except LangDetectException:
        return "unknown"


# ── Load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig")
print(f"Loaded {len(df)} rows")

# ── Detect ────────────────────────────────────────────────────────────────────
print("Detecting languages... (this may take a few minutes)")
df["language"] = df["text"].apply(detect_language)

print("\nLanguage distribution:")
print(df["language"].value_counts())

# ── Filter — keep only useful languages ───────────────────────────────────────
KEEP = {"Tamil", "Tanglish", "Hindi", "English", "Malayalam"}
df = df[df["language"].isin(KEEP)]

# ── Save ──────────────────────────────────────────────────────────────────────
df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
print(f"\nSaved {len(df)} rows → {OUTPUT_PATH}")
print(df["language"].value_counts())