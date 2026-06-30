# scripts/build_seed_dataset.py
import os
import random
import pandas as pd

random.seed(42)

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR   = os.path.abspath(os.path.join(BASE_DIR, ".."))
OUTPUT_PATH   = os.path.join(PROJECT_DIR, "data", "labeled", "labeled_dataset.csv")
EXISTING_PATH = os.path.join(PROJECT_DIR, "data", "labeled", "auto_labeled.csv")

os.makedirs(os.path.join(PROJECT_DIR, "data", "labeled"), exist_ok=True)

label_map = {"safe": 0, "mild_toxic": 1, "hate_speech": 2, "severe": 3}

# ═══════════════════════════════════════════════════════════════════════════════
# TAMIL SEEDS
# ═══════════════════════════════════════════════════════════════════════════════
tamil_safe = [
    "நீங்கள் எப்படி இருக்கீங்க?",
    "இன்று வானிலை நன்றாக இருக்கிறது",
    "உங்கள் வேலை எப்படி போகிறது?",
    "நாளை நாம் சந்திக்கலாம்",
    "படம் மிகவும் நன்றாக இருந்தது",
    "பள்ளி நேரம் என்ன?",
    "உங்கள் குடும்பம் எப்படி?",
    "இந்த உணவு சுவையாக இருக்கிறது",
    "நன்றி மிக்க நன்றி",
    "நாளை வருகிறேன்",
    "இன்று சாலை நெரிசல் அதிகமாக இருந்தது",
    "புத்தகம் மிகவும் சுவாரஸ்யமாக இருந்தது",
    "உங்கள் பிறந்தநாள் எப்போது?",
    "தேர்வு முடிவுகள் நன்றாக வந்தது",
    "விளையாட்டு போட்டி நேரடியாக பார்த்தோம்",
    "திருமண விழா மிகவும் அழகாக இருந்தது",
    "மழை வந்தால் வெளியே போக வேண்டாம்",
    "அம்மா சமையல் மிகவும் சுவையாக இருக்கும்",
    "நண்பர்களுடன் சுற்றுலா போனோம்",
    "கோயிலுக்கு போய் வந்தோம்",
]

tamil_mild = [
    "நீ முட்டாள்",
    "உனக்கு ஒன்றும் தெரியாது",
    "போடா வேலைக்கு",
    "எரிச்சலா இருக்க",
    "வாயை மூடு",
    "உன்னால முடியாது",
    "சும்மா இரு",
    "தொந்தரவு பண்ணாதே",
    "அலட்டிக்காதே",
    "உனக்கு இது புரியாது",
    "பயனில்லாதவன்",
    "வேலையில்லாத வேலை செய்கிறாய்",
    "உன் பேச்சு யாருக்கும் தேவையில்லை",
    "நீ செய்வதெல்லாம் தப்பு",
    "இவ்வளவு சின்ன விஷயம் தெரியாதா",
    "மொத்தமே தரமற்றவன்",
    "போய் வேற வேலை பாரு",
    "இது உனக்கு பொருந்தாது",
    "உன் யோசனை முட்டாள்தனமானது",
    "வெட்கமே இல்லாமல் பேசுகிறாய்",
]

tamil_hate = [
    "நீ ஒரு ஆட்டு மந்தை",
    "உன்னால ஒரு பயனும் இல்லை நீ வாழ்க்கையில் தோல்வியடைவாய்",
    "உன் வகையினர் இங்கு வேண்டாம்",
    "நீ இந்த குழுவில் இருக்கக் கூடாது",
    "உன் சாதி ஆட்கள் எல்லாம் ஒரே மாதிரி",
    "வெளியே போ உனக்கு இங்கு இடம் இல்லை",
    "உன்னை யாரும் விரும்பவில்லை",
    "நீ ஒரு பயலு உன்னால ஒண்ணும் ஆகாது",
    "உன்னோட முகம் பார்க்கவே வெறுப்பாக இருக்கு",
    "இந்த நாயை யாரும் நம்பவே வேண்டாம்",
    "உன் ஜாதியினர் எல்லாம் இப்படித்தான் இருப்பார்கள்",
    "நீ இங்கே இருக்கவே தகுதியில்லாதவன்",
    "உன்னை பார்க்கவே அருவருப்பாக இருக்கிறது",
    "உன் இனத்தவர்கள் எல்லாம் ஒரே மாதிரி பயனற்றவர்கள்",
    "இவர்களை இங்கிருந்து விரட்ட வேண்டும்",
    "உன்னை யாரும் மதிக்க மாட்டார்கள்",
    "உன் மதத்தினர் எல்லாம் வேற்றுமையை விதைக்கிறார்கள்",
    "உன்னோட வாழ்க்கை ஒரு தோல்வி மட்டுமே",
    "உன் குடும்பமே வெட்கப்படுவார்கள் உன்னால",
    "இம்மாதிரி ஆட்களை சமூகம் ஏற்க மாட்டாது",
]

tamil_severe = [
    "உன்னை பாத்துக்கிறேன் நாளைக்கு நான் உன்னை விட மாட்டேன்",
    "உனக்கு என்ன ஆகுமென்று தெரியும் கவனமாக இரு",
    "நீ வீட்டை விட்டு வெளியே வந்தால் பார்க்கிறேன்",
    "உன் உயிர் போகும் கவலைப்படாதே",
    "நாளை உன்னை கண்டுபிடிப்பேன் தப்பிக்க முடியாது",
    "உன்னையும் உன் குடும்பத்தையும் விட மாட்டேன்",
    "ஒரே ஒரு வாய்ப்பு மட்டும் கொடுக்கிறேன் இல்லாவிட்டால்",
    "உனக்கு நடக்கப் போவதை நீயே பார்ப்பாய்",
    "உன்னை தேடி வருவேன் எங்கே ஓடினாலும்",
    "கொலை செய்வேன் என்று சொல்கிறேன் நம்பு",
    "உன் வீட்டு முகவரி எனக்கு தெரியும்",
    "இன்று இரவே உன்னை பார்க்கிறேன்",
    "உனக்கு இப்போதே எச்சரிக்கை கொடுக்கிறேன்",
    "உன்னை சும்மா விட மாட்டேன் நினைத்துக்கோ",
    "தப்பி ஓடினாலும் உன்னை கண்டுபிடிப்பேன்",
]

# ═══════════════════════════════════════════════════════════════════════════════
# TANGLISH SEEDS
# ═══════════════════════════════════════════════════════════════════════════════
tanglish_safe = [
    "neenga epdi irukeenga?",
    "indha padam romba nalla irundhuchu",
    "naalaiku paarkalama?",
    "saapadu super ah irundhuchu",
    "vanakkam bro epdi iruka?",
    "enna vishayam sollu",
    "nalla news sollu machan",
    "yarellam varuvaanga naalaiku?",
    "area la puthusa enna nadakuthu?",
    "exam result nalla vandhucha?",
    "amma cooking romba taste ah irukum",
    "friendsa kooda outing ponen",
    "match live ah paathoam",
    "kalyanam super ah nadandhuchu",
    "semma fun ah irundhuchu da",
    "rain varuchu pola iruku",
    "koil poitu vandhoam",
    "puthusa enna padikara?",
    "project work epdi poidhu?",
    "weekend free ah iruka?",
]

tanglish_mild = [
    "dei muttaal fellow",
    "unakku onnume theriyaadu",
    "po da velaikku",
    "erichal ah iruku unna paakka",
    "vaaya moodu",
    "unnala mudiyaadu",
    "summa iru da",
    "thollaiya panna vendam",
    "otha figure nu theriyum",
    "unaku puriyaadu idu",
    "payan illa unala",
    "romba over ah pesaadha",
    "un peschu yarukum vendam",
    "ellame thappuve panra",
    "intha vishayam unaku theriyuma",
    "tharamilla figure",
    "po vere velai paaru",
    "unakku pottaadu idu",
    "mottai logic pesaadha",
    "veram pudichidhu unnoda basha",
]

tanglish_hate = [
    "un maari aalunga ingae vendam",
    "unnala oru prayojaname illai nee tholviyae adaivai",
    "un jaathi aalunga ellam ippadi thaan",
    "nee indha group la irukakaadaadu",
    "ungala maari peopleku idam illai",
    "po da ungaluku ingae idam illai",
    "unnai yarume virumbamaathaanga",
    "nee oru kozhai unnala onnum aagaadu",
    "un muga paakavae veruppa iruku",
    "indha naayai yarume namba vendam",
    "un community ellam ippadi thaan iruppaanga",
    "nee ingae irukka thagatiyillaadhavan",
    "un maatham aalunga ellam problem create panraanga",
    "unnai society accept pannaathe",
    "ingae irundhu po unna maadhiri aalunga vendam",
    "un family yum unna pathi vekangappaduvaanga",
    "un vaazhkai oru waste",
    "nee pirandhathe thappa",
    "un race ellame ippadi thaan",
    "unnai yarume mattikkamaathaanga",
]

tanglish_severe = [
    "unnai paathukiren naalaikku viduva maaten",
    "unakku enna aagum theriyum kavanamai iru",
    "veetai vittu veliyae vandha paarkiren",
    "un uyire pogum kavalapadaadha",
    "naalai unnai kandupidipean tappika mudiyaadu",
    "unnayum un kutumbathayum vida maaten",
    "oru vaippu mattum kudukirean illati paaru",
    "unakku nadakka povathai neeyae paarpai",
    "unnai thedi varuvan engae odinalum",
    "kolai pannuven nu solliren namba",
    "un vedu address enakku theriyum",
    "indha iravu unnai paarkiren",
    "ipove warning kudukirean",
    "unnai sappa vida maaten ninaikko",
    "tappiyodinalum unnai kandupidipean",
    "un kita varuven ready ah iru",
    "last chance idu thappi paartha",
    "un life mudikka ready ah irukean",
]

# ═══════════════════════════════════════════════════════════════════════════════
# HINDI SEEDS
# ═══════════════════════════════════════════════════════════════════════════════
hindi_safe = [
    "आप कैसे हैं?",
    "आज मौसम अच्छा है",
    "कल मिलते हैं",
    "खाना बहुत अच्छा था",
    "धन्यवाद आपकी मदद के लिए",
    "स्कूल कब है?",
    "परिवार कैसा है?",
    "मुझे यह पसंद है",
    "बहुत अच्छा काम किया",
    "ठीक है कोई बात नहीं",
    "आज बहुत मज़ा आया",
    "नई फिल्म देखी बहुत अच्छी थी",
    "आपका जन्मदिन कब है?",
    "परीक्षा का परिणाम अच्छा रहा",
    "दोस्तों के साथ घूमने गए",
    "शादी की पार्टी बहुत अच्छी रही",
    "बारिश हो रही है बाहर मत जाओ",
    "माँ का खाना सबसे अच्छा होता है",
    "मंदिर से आकर अच्छा लगा",
    "सप्ताहांत में क्या करोगे?",
]

hindi_mild = [
    "तुम बेकार हो",
    "बंद करो यह बकवास",
    "तुम्हें कुछ नहीं पता",
    "चुप रहो",
    "यहाँ से जाओ",
    "तुमसे नफरत है",
    "बड़ी बेशर्मी है",
    "मूर्ख कहीं के",
    "शर्म नहीं आती",
    "तुम्हारा दिमाग खराब है",
    "तुम पर भरोसा नहीं किया जा सकता",
    "कुछ भी ढंग से नहीं करते",
    "हर काम में गड़बड़ करते हो",
    "तुम्हारी सोच बिल्कुल गलत है",
    "इतनी छोटी बात भी नहीं समझते",
    "तुम्हारी बातें किसी काम की नहीं",
    "जाओ कोई और काम करो",
    "तुम्हें यह शोभा नहीं देता",
    "बेकार की बातें करते रहते हो",
    "तुम्हारी वजह से सब परेशान हैं",
]

hindi_hate = [
    "तुम जैसे लोगों को यहाँ नहीं रहना चाहिए",
    "तुम्हारी जाति के लोग सब एक जैसे होते हैं",
    "तुम्हें यहाँ से निकाल दो",
    "तुम्हारे जैसे लोगों का यहाँ काम नहीं",
    "यह देश तुम्हारे लिए नहीं है",
    "तुम्हारी औकात नहीं है यहाँ रहने की",
    "तुम्हारे समुदाय को बाहर निकालो",
    "ऐसे लोग हमारे बीच में नहीं चाहिए",
    "तुम्हारी वजह से सब बर्बाद हो रहा है",
    "तुम लोग यहाँ से चले जाओ",
    "तुम्हारे मज़हब के लोग सब एक जैसे होते हैं",
    "तुम्हारे जैसे लोग देश के लिए खतरा हैं",
    "यह समाज तुम्हें स्वीकार नहीं करेगा",
    "तुम्हारे परिवार को भी शर्म आनी चाहिए",
    "तुम्हारी नस्ल ही ऐसी है",
    "तुम यहाँ रहने के लायक नहीं हो",
    "तुम्हारे लोगों को यहाँ से भगाना चाहिए",
    "ऐसे लोगों को देश में जगह नहीं मिलनी चाहिए",
    "तुम्हारी वजह से समाज गंदा हो रहा है",
    "तुम जैसे लोग कहीं के नहीं रहते",
]

hindi_severe = [
    "तुम्हें ढूंढ लूंगा और मजा चखाऊंगा",
    "कल तक का समय है वरना देख लेना",
    "जान से मार दूंगा समझे",
    "अपनी जिंदगी के बारे में सोचो बचेगी नहीं",
    "घर से निकले तो देख लेना क्या होगा",
    "तुम्हारे घरवालों को भी नहीं छोड़ूंगा",
    "पुलिस भी बचा नहीं पाएगी तुम्हें",
    "तुम्हारा पता मुझे पता है आज रात देखना",
    "आखिरी चेतावनी है इसके बाद देख लेना",
    "तुम्हें जिंदा नहीं छोड़ूंगा",
    "तुम भाग भी नहीं सकते मैं ढूंढ लूंगा",
    "तुम्हारी गर्दन पर हाथ रखूंगा",
    "घर आकर बताऊंगा मज़ा",
    "तैयार रहो आज रात आ रहा हूं",
    "यह आखिरी मौका है मानो वरना",
]

# ═══════════════════════════════════════════════════════════════════════════════
# ENGLISH SEEDS
# ═══════════════════════════════════════════════════════════════════════════════
english_safe = [
    "How are you doing today?",
    "The weather is nice today",
    "Let's meet tomorrow",
    "The food was really good",
    "Thank you so much for helping",
    "What time is school?",
    "How is your family?",
    "I really liked that movie",
    "Great job on the project",
    "No worries at all",
    "See you later",
    "Have a great day",
    "The match was so exciting to watch",
    "Happy birthday to you",
    "Congratulations on your achievement",
    "The trip was absolutely wonderful",
    "I enjoyed the concert last night",
    "Your presentation was very impressive",
    "Hope you feel better soon",
    "Looking forward to seeing you",
]

english_mild = [
    "you are so stupid",
    "shut up nobody cares",
    "you don't know anything",
    "stop being so annoying",
    "you are useless",
    "get out of here",
    "nobody likes you",
    "you are so dumb",
    "stop posting this garbage",
    "you are the worst",
    "go away loser",
    "you make me sick",
    "your opinion is worthless",
    "stop talking you are embarrassing yourself",
    "you are such a clown",
    "everything you do is wrong",
    "you are a complete joke",
    "nobody wants to hear from you",
    "you are the most annoying person",
    "please just stop existing online",
]

english_hate = [
    "you and your kind don't belong here",
    "people like you should be removed",
    "your community is ruining everything",
    "you should leave this country",
    "nobody wants your type here",
    "you are a disgrace to everyone",
    "your whole family is worthless trash",
    "you will never amount to anything",
    "everyone hates you and they should",
    "your existence is a waste of space",
    "we don't want you in this group get out",
    "you are inferior and always will be",
    "your race has always been a problem",
    "people like you are destroying society",
    "your kind has no place in this world",
    "you should be ashamed of what you are",
    "your community brings nothing but trouble",
    "you are the reason things are getting worse",
    "no one from your background deserves respect",
    "your entire group should be removed from here",
]

english_severe = [
    "I will find you and make you pay",
    "I know where you live and I am coming",
    "you better watch your back tonight",
    "I will hurt you badly if you don't stop",
    "this is your last warning or else",
    "you and your family are not safe",
    "I will kill you if you show up tomorrow",
    "you cannot hide from me I will find you",
    "meet me outside and see what happens",
    "I am going to destroy your life completely",
    "I have your address and I am on my way",
    "say that one more time and I will end you",
    "you have 24 hours to leave or else",
    "I will make sure you regret this",
    "your family will pay for what you did",
    "I am watching you every move you make",
    "there is nowhere you can run from me",
    "I will come for you when you least expect it",
    "consider this your final warning",
    "I know your schedule and I will be there",
]

# ═══════════════════════════════════════════════════════════════════════════════
# BUILD RECORDS
# ═══════════════════════════════════════════════════════════════════════════════
records = []

AUGMENT_SUFFIXES = {
    "Tamil":    [" da", " di", " pa", " nu", " ல", " யா", ""],
    "Tanglish": [" da", " bro", " machaan", " seriously", " ok", " nu", ""],
    "Hindi":    [" यार", " भाई", " जी", " ना", " तो", ""],
    "English":  [" man", " seriously", " ok", " now", " honestly", ""],
}

def add_records(texts: list, label: str, language: str, augment: int = 3):
    suffixes = AUGMENT_SUFFIXES.get(language, [""])
    for text in texts:
        records.append({
            "text":     text,
            "label":    label,
            "label_id": label_map[label],
            "language": language,
            "platform": "seed",
        })
        for _ in range(augment):
            aug = text + random.choice(suffixes)
            records.append({
                "text":     aug.strip(),
                "label":    label,
                "label_id": label_map[label],
                "language": language,
                "platform": "augmented",
            })

# Tamil
add_records(tamil_safe,    "safe",        "Tamil")
add_records(tamil_mild,    "mild_toxic",  "Tamil")
add_records(tamil_hate,    "hate_speech", "Tamil")
add_records(tamil_severe,  "severe",      "Tamil")

# Tanglish
add_records(tanglish_safe,    "safe",        "Tanglish")
add_records(tanglish_mild,    "mild_toxic",  "Tanglish")
add_records(tanglish_hate,    "hate_speech", "Tanglish")
add_records(tanglish_severe,  "severe",      "Tanglish")

# Hindi
add_records(hindi_safe,    "safe",        "Hindi")
add_records(hindi_mild,    "mild_toxic",  "Hindi")
add_records(hindi_hate,    "hate_speech", "Hindi")
add_records(hindi_severe,  "severe",      "Hindi")

# English
add_records(english_safe,    "safe",        "English")
add_records(english_mild,    "mild_toxic",  "English")
add_records(english_hate,    "hate_speech", "English")
add_records(english_severe,  "severe",      "English")

df_seed = pd.DataFrame(records)

# ═══════════════════════════════════════════════════════════════════════════════
# MERGE WITH EXISTING LABELED DATA
# ═══════════════════════════════════════════════════════════════════════════════
try:
    df_existing = pd.read_csv(EXISTING_PATH, encoding="utf-8-sig")
    df_existing = df_existing[df_existing["label"].notna()]
    df_existing = df_existing[df_existing["label"].astype(str).str.strip() != ""]
    if "label_id" not in df_existing.columns:
        df_existing["label_id"] = df_existing["label"].map(label_map)
    df_final = pd.concat([df_seed, df_existing], ignore_index=True)
    print(f"Merged with existing auto_labeled: {len(df_existing)} rows")
except FileNotFoundError:
    df_final = df_seed
    print("No existing dataset found — using seed only")
except Exception as e:
    df_final = df_seed
    print(f"Could not load existing dataset ({e}) — using seed only")

# ═══════════════════════════════════════════════════════════════════════════════
# CLEAN AND SAVE
# ═══════════════════════════════════════════════════════════════════════════════
df_final.drop_duplicates(subset=["text"], inplace=True)
df_final.reset_index(drop=True, inplace=True)
df_final.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

print(f"\nFinal dataset saved → {OUTPUT_PATH}")
print(f"\nLabel distribution:")
print(df_final["label"].value_counts())
print(f"\nLanguage distribution:")
print(df_final["language"].value_counts())
print(f"\nTotal rows: {len(df_final)}")