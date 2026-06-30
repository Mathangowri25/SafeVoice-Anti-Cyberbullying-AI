import os
import re
import nltk
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# ── Download NLTK data if not already present ─────────────────────────────────
nltk.download("punkt",         quiet=True)
nltk.download("punkt_tab",     quiet=True)
nltk.download("stopwords",     quiet=True)

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
INPUT_PATH  = os.path.join(PROJECT_DIR, "data", "processed", "step2_with_language.csv")
OUTPUT_PATH = os.path.join(PROJECT_DIR, "data", "processed", "step3_preprocessed.csv")

# ── Stopwords ─────────────────────────────────────────────────────────────────
english_stopwords = set(stopwords.words("english"))

# Common Tanglish/Tamil filler words written in Roman script
tanglish_stopwords = {
    "da", "di", "la", "nu", "na", "pa", "ba", "va", "ra",
    "ah", "oh", "eh", "ha", "bro", "anna", "akka", "appa", "amma",
    "yaar", "macha", "machaan", "dei", "dey", "aiyo", "ayyo",
    "seri", "sari", "ok", "okay", "lol", "haha", "hehe",
}

# ── Preprocessors ─────────────────────────────────────────────────────────────
def preprocess_english(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    tokens = word_tokenize(text)
    tokens = [t for t in tokens if t not in english_stopwords and len(t) > 1]
    return " ".join(tokens)


def preprocess_tamil(text: str) -> str:
    # Keep Tamil Unicode (\u0B80–\u0BFF) + ASCII printable range
    text = re.sub(r'[^\u0B80-\u0BFF\u0020-\u007E\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def preprocess_hindi(text: str) -> str:
    # Keep Devanagari Unicode (\u0900–\u097F) + ASCII printable range
    text = re.sub(r'[^\u0900-\u097F\u0020-\u007E\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def preprocess_malayalam(text: str) -> str:
    # Keep Malayalam Unicode (\u0D00–\u0D7F) + ASCII printable range
    text = re.sub(r'[^\u0D00-\u0D7F\u0020-\u007E\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def preprocess_tanglish(text: str) -> str:
    # Tanglish is Roman-script Tamil — lowercase + remove punctuation,
    # strip Tanglish filler words, keep meaningful tokens
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    tokens = word_tokenize(text)
    tokens = [
        t for t in tokens
        if t not in english_stopwords
        and t not in tanglish_stopwords
        and len(t) > 1
    ]
    return " ".join(tokens)


def preprocess_row(row) -> str:
    text = str(row["text"]).strip()
    lang = str(row.get("language", "English"))

    if lang == "English":
        return preprocess_english(text)
    elif lang == "Tamil":
        return preprocess_tamil(text)
    elif lang == "Hindi":
        return preprocess_hindi(text)
    elif lang == "Malayalam":
        return preprocess_malayalam(text)
    elif lang == "Tanglish":
        return preprocess_tanglish(text)
    else:
        # For any other detected language just do basic cleanup
        text = re.sub(r'\s+', ' ', text).strip()
        return text


# ── Load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig")
print(f"Loaded {len(df)} rows")

# ── Preprocess ────────────────────────────────────────────────────────────────
print("Preprocessing text...")
df["text_clean"] = df.apply(preprocess_row, axis=1)

# Drop rows that became empty after preprocessing
df = df[df["text_clean"].str.strip().str.len() >= 3]

# ── Save ──────────────────────────────────────────────────────────────────────
df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
print(f"\nSaved {len(df)} preprocessed rows → {OUTPUT_PATH}")
print(df[["text", "text_clean", "language"]].head(10).to_string())