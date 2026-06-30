import os
import re
import pandas as pd

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
INPUT_PATH  = os.path.join(PROJECT_DIR, "data", "processed", "final_unlabeled.csv")
OUTPUT_DIR  = os.path.join(PROJECT_DIR, "data", "labeled")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "auto_labeled.csv")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig")
print(f"Loaded {len(df)} rows")

# ═══════════════════════════════════════════════════════════════════════════════
# KEYWORD SEED LISTS
# ═══════════════════════════════════════════════════════════════════════════════

# ── ENGLISH ───────────────────────────────────────────────────────────────────
severe_en = [
    # Direct death / kill threats
    "kill", "killing", "killed", "i will kill", "i'll kill", "gonna kill",
    "want to kill", "going to kill", "kill you", "kill them", "kill him",
    "kill her", "kill all", "kill myself",
    "murder", "murdered", "murderer", "murdering",
    "slaughter", "slaughtered", "massacre", "massacred", "mass murder",
    "execute", "execution", "executed", "firing squad",
    "behead", "beheading", "decapitate", "decapitation",
    "genocide", "ethnic cleansing", "exterminate", "wipe out",
    # Death wishes
    "die", "you will die", "you're going to die", "should die",
    "deserve to die", "hope you die", "wish you were dead",
    "drop dead", "go die", "just die", "die already",
    "you are dead", "you're dead", "dead meat", "as good as dead",
    # Physical violence
    "rape", "gang rape", "i will rape", "gonna rape", "rape you",
    "molest", "molestation", "molested", "grope",
    "assault", "physical assault", "sexually assault",
    "stab", "stabbing", "stabbed", "knife you", "shank",
    "shoot", "shoot you", "shoot him", "shoot her", "gun down",
    "shot dead", "open fire", "fire at",
    "beat", "beat you up", "beat him", "beat to death", "beat senseless",
    "punch", "punch you", "smash your face", "break your bones",
    "strangle", "choke", "choke you", "strangle you",
    "torture", "tortured", "torturing",
    "burn alive", "set on fire", "light you on fire",
    "bury alive", "drown you", "suffocate",
    # Weapons / explosives
    "bomb", "bombing", "suicide bomb", "suicide bomber",
    "blast", "explosion", "blow up", "blow you up",
    "ied", "improvised explosive",
    "acid attack", "throw acid", "acid on your face",
    "poison", "poisoned", "lace your drink",
    # Suicide / self-harm incitement
    "kill yourself", "kys", "end your life", "end it all",
    "hang yourself", "go hang", "slit your wrist", "slit your throat",
    "jump off", "jump in front", "overdose", "take pills and die",
    "drink bleach", "eat glass",
    "suicide", "suicidal", "self harm", "self-harm", "self mutilate",
    "nobody will miss you", "world is better without you",
    "your family is better off without you",
    # Stalking / pursuit threats
    "hunt you down", "come after you", "find you", "track you down",
    "know where you live", "i know your address", "watching you",
    "follow you home", "wait for you outside",
    "destroy you", "finish you", "finish you off",
    "deal with you", "take care of you", "make you pay",
    "you won't get away", "nowhere to hide", "no escape for you",
    # Sexual violence / exploitation
    "child abuse", "child sexual abuse", "csam", "cp",
    "sex trafficking", "human trafficking",
    "force yourself on", "non consensual",
]

hate_en = [
    # Cognitive insults
    "stupid", "stupidity", "idiot", "idiotic", "moron", "moronic",
    "imbecile", "retard", "retarded", "dumb", "dumbass", "dumb fuck",
    "fool", "foolish", "brainless", "mindless", "clueless", "senseless",
    "brain dead", "braindead", "no brain", "empty skull", "hollow head",
    # Worthlessness / dehumanization
    "worthless", "worthless piece", "useless", "useless piece of",
    "waste of space", "waste of oxygen", "waste of skin",
    "you don't deserve to live", "shouldn't have been born",
    "mistake", "accident", "your parents regret you",
    # Animal comparisons
    "dog", "bitch", "mutt", "mongrel",
    "pig", "swine", "hog",
    "animal", "beast", "creature",
    "parasite", "vermin", "cockroach", "pest", "rodent",
    "monkey", "ape", "gorilla",
    "donkey", "jackass", "mule",
    "rat", "snake", "reptile", "leech", "bloodsucker",
    "filth", "dirt", "scum of the earth",
    # Gendered / sexual slurs
    "bastard", "son of a bitch", "son of a whore",
    "whore", "slut", "hoe", "thot", "skank",
    "prostitute", "call girl",
    "cuck", "simp", "incel",
    "man whore", "male slut",
    # General abuse
    "scum", "trash", "garbage", "rubbish", "junk",
    "loser", "failure", "born loser", "epic failure",
    "coward", "spineless", "gutless", "pathetic loser",
    "piece of shit", "pos", "piece of crap",
    "go to hell", "rot in hell", "burn in hell",
    "get lost", "fuck off", "piss off", "shove it",
    "shut up", "shut your mouth", "shut your face",
    "no one wants you", "nobody likes you", "everyone hates you",
    # Identity-based hate
    "racist", "racism", "racial slur",
    "bigot", "bigotry", "sexist", "sexism",
    "misogynist", "misogyny", "misandrist",
    "casteist", "casteism", "untouchable", "lower caste",
    "islamophobia", "islamophobic", "hindu hater", "christian hater",
    "homophobic", "transphobic", "queer hater",
    "go back to your country", "not welcome here", "outsider",
    "foreigner go home", "your kind", "your people",
    # Extremism labels used as slurs
    "terrorist", "jihadi", "jihadist", "extremist", "fanatic",
    "radical", "fundamentalist", "insurgent",
    "traitor", "spy", "enemy of the state",
]

mild_en = [
    # Negative descriptors
    "annoying", "irritating", "frustrating", "infuriating",
    "boring", "tedious", "dull", "mind-numbing",
    "pathetic", "sad", "pitiful", "pitiable",
    "disgusting", "gross", "nasty", "revolting", "repulsive",
    "awful", "terrible", "horrible", "horrendous", "dreadful", "atrocious",
    "bad", "very bad", "so bad", "worst", "the worst",
    "ugly", "hideous", "eyesore",
    "cringe", "cringey", "cringeworthy", "embarrassing",
    "lame", "weak", "feeble",
    # Dismissal
    "overrated", "hyped", "all hype", "disappointing", "letdown",
    "nobody cares", "who asked", "no one asked", "who cares",
    "irrelevant", "not important", "doesn't matter",
    "stop talking", "stop posting", "please stop",
    "unfollow", "block you", "mute you",
    # Character attacks
    "fake", "fraud", "con", "scammer", "swindler",
    "liar", "lying", "habitual liar",
    "hypocrite", "two-faced", "backstabber", "double standard",
    "attention seeker", "drama queen", "clout chaser",
    "clown", "joker", "buffoon", "class clown",
    "show off", "poser", "pretender", "wannabe",
    # Mild emotional venting
    "hate this", "hate you", "hate them", "i hate", "really hate",
    "dislike", "strongly dislike", "detest", "despise", "loathe",
    "can't stand", "can't stand you", "can't tolerate",
    "so annoying", "so irritating", "drives me crazy",
    "sick of", "tired of", "fed up with",
]

# ── TAMIL (Unicode script) ────────────────────────────────────────────────────
severe_ta = [
    # Kill / death threats
    "கொல்", "கொல்வேன்", "கொல்லுவேன்", "கொல்லுவோம்",
    "கொலை", "கொலை செய்", "கொலை செய்வேன்", "கொலை செய்யுவேன்",
    "செத்துபோ", "செத்து போ", "சாகு", "சாகடிப்பேன்",
    "இறந்து போ", "மரணம் வரும்", "உன் உயிர் போகும்",
    "தீயில் போட்டு", "தீ வைப்பேன்", "எரித்து விடுவேன்",
    "கொலைவெறி", "படுகொலை", "வெட்டுவேன்", "குத்துவேன்",
    "தலை வெட்டுவேன்", "கழுத்தை அறுப்பேன்",
    # Sexual violence
    "பலாத்காரம்", "பலாத்காரம் செய்வேன்", "கற்பழிப்பு",
    "கற்பழிப்பு செய்வேன்", "ரேப்", "ரேப் செய்வேன்",
    "பாலியல் வன்கொடுமை", "உடலை தொடுவேன்",
    # Weapons / explosives
    "குண்டு வெடிக்க வைப்பேன்", "குண்டு போட்டு",
    "வெடி குண்டு", "வெடிக்க வைப்பேன்",
    "தாக்குதல்", "தாக்குவேன்", "அடித்து கொல்வேன்",
    # Stalking / threats
    "உன்னை விட மாட்டேன்", "உன்னை தேடி வருவேன்",
    "உன் வீடு தெரியும்", "உன்னை பார்த்துக்கொள்வேன்",
    "உயிரை எடுப்பேன்", "உயிரோடு விட மாட்டேன்",
    "அச்சுறுத்தல்", "மிரட்டுகிறேன்", "மிரட்டல்",
    # Suicide incitement
    "தூக்கிட்டுக்கோ", "விஷம் குடி", "தண்ணீரில் குதி",
    "உயிரை மாய்த்துக்கோ", "யாரும் உன்னை நினைக்க மாட்டோம்",
    "நீ இல்லாமல் உலகம் நல்லது",
]

hate_ta = [
    # Cognitive insults
    "முட்டாள்", "முட்டாளே", "மடையன்", "மடையள்", "மடமை",
    "பேதை", "அறிவிலி", "அறிவற்றவன்", "புத்தியில்லாதவன்",
    "வெறியன்", "வெறியர்", "சித்தி கெட்டவன்",
    "பைத்தியம்", "பைத்தியக்காரன்", "மனநோயாளி",
    "தலை இல்லாதவன்", "கழுதை மூளை",
    # Animal comparisons
    "நாய்", "நாயே", "பன்றி", "பன்றியே", "கழுதை",
    "குரங்கு", "பாம்பு", "எலி", "பல்லி", "பூரான்",
    "காட்டு மிராண்டி", "மிருகம்",
    # Gendered / sexual slurs
    "தேவடியா", "தேவடியாள்", "விபச்சாரி",
    "ஓமாலி", "புண்டைமவன்", "தாயோளி", "தந்தையோளி",
    "சுன்னி", "ஓழ் மவன்",
    # General abuse
    "கயவன்", "கயவர்", "நயவஞ்சகன்", "வஞ்சகன்",
    "பயலே", "பய", "கோழை", "கோழைத்தனம்",
    "தரமற்றவன்", "தரமற்றவள்", "நீசன்", "அற்பன்",
    "போய் செத்துக்கோ", "வாயை மூடு", "நரகத்தில் போ",
    "யாரும் உன்னை வேண்டாம்", "உன்னை யாரும் நேசிக்கவில்லை",
    "ஊர்க்கு ஆகாதவன்",
    # Caste / identity hate
    "ஜாதி கேவலம்", "சாதி திட்டு", "தாழ்த்தப்பட்டவன்",
    "தலித் திட்டு", "மேல் ஜாதி திமிர்",
    "வெளியே போ", "உன் இடம் இங்கே இல்லை",
    "மதவெறியன்", "இனவெறியன்",
]

mild_ta = [
    # Negative feelings
    "வெறுப்பு", "வெறுக்கிறேன்", "வெறுக்கிறேன் உன்னை",
    "கோபம்", "கோபமாக இருக்கிறது", "எரிச்சல்", "எரிச்சலாக இருக்கு",
    "அலுப்பு", "சலிப்பு", "கோமாளி", "கோமாளித்தனம்",
    "அசிங்கம்", "அசிங்கமான", "மோசம்", "படுமோசம்",
    "சோர்வு", "கஷ்டமான", "மிகவும் மோசம்",
    # Character attacks
    "பொய்யன்", "பொய்யி", "வஞ்சகன்", "போலி",
    "நம்பிக்கை இல்லாதவன்", "நம்பகமற்றவன்",
    "காட்டிக்கொடுத்தவன்", "துரோகி",
    "விஷமி", "குறும்பன்", "கள்ளன்",
    # Dismissal
    "யாரும் கேட்கவில்லை", "யாருக்கும் தேவையில்லை",
    "பேசாமல் இரு", "தேவையில்லாம் பேசாதே",
    "அதிக பேச்சு", "வாயை மூடு",
    "பயனற்றவன்", "தேவையற்றவன்",
]

# ── TANGLISH (Tamil in Roman script) ─────────────────────────────────────────
severe_tl = [
    # Kill / death threats
    "kolai", "kolai pannu", "kolai pannuven", "kolai pannrom",
    "kolluvean", "kolluven", "kollurom", "kolu",
    "sethu po", "sethupo", "sethuko", "saagadi",
    "saaga vaa", "saaguvai", "saagadichchu",
    "uriye eduthukkuven", "uyire eduppean", "uyire eduppen",
    "unna mudippean", "unna mudikiren",
    "thalaye vettuven", "kazhuthai aruppen",
    "erichi viduven", "thee vaippen",
    "adichu koluven", "odaichiduvean",
    # Sexual violence
    "rape pannu", "rape pannuven", "rape panna poren",
    "balatkaaram", "kaarpazhippu pannu","oombatha","sappu",
    "unna touch pannuven", "unna vidiya maaten",
    # Weapons / explosives
    "bomb vaippean", "bomb pottiduvean",
    "thakku", "thakkuven", "thakki poda",
    "katthi vaippean", "katthi kitu varuven",
    "gun vaippean", "sutta viduven",
    # Stalking / pursuit threats
    "unna theditu varuven", "unna viduva maaten",
    "un vedu theriyum", "un address theriyum",
    "unnai paakitu iruken", "follow pannuven",
    "threat pannuven", "mirattuvean", "mirattal",
    "unna parthukuven", "koodave varuven",
    "viduva maaten da", "viduva maatean","munda",
    # Suicide incitement
    "thookidukkuven", "thooki podu",
    "visham kudikka solluven", "visham kudichi saa",
    "thannila thoppidu", "uyirai maithukko",
    "yarumae miss pannuvaangala", "unna yarume vendam",
    "nee illama ulagam nalladu",
]

hate_tl = [
    # Cognitive insults
    "muttaal", "muttaale", "muttaalae", "muttaaloda",
    "madayan", "madayal", "madamai",
    "bethai", "bethaiye", "arivillaadavan",
    "veriyan", "veriyanae", "loosu", "loosupaya",
    "paiththiyam", "paithiyakaaran", "pisaru",
    "thalai illaadhavan", "buddhi illaadhavan",
    "kalai illa", "arivil paiththiyam",
    # Animal comparisons
    "naaye", "naai", "naaikku porandha",
    "panni", "panniye", "panni maadhiri",
    "kazhutha", "kazhuthai maadhiri",
    "kurangu", "kurangukkum keezhae",
    "pambu", "eli", "palli", "pooran",
    # Gendered / sexual slurs
    "thevdiya", "thevdiyaa", "thevdiya pasanga",
    "omaala", "omala", "ombodu",
    "pundaimavan", "pundaikos", "sunni",
    "thaayoli", "thanthayoli", "thaayoli pasanga",
    "veshya", "veshyapayal",
    # General abuse
    "palayan", "palayane", "kayavan",
    "kozhai", "kozhaiya", "kozhai payal",
    "pisasu", "pisasuu",
    "tharamillaadavan", "tharamilla payal",
    "yaarum illaadavan", "yaarum unna vendam",
    "vaaya moodu", "poi nee", "engayo po",
    "po nee", "po da", "po di",
    "jaathi kevalama", "saatiyae", "jaathiya paaru",
    "thalaiku mattume layikku",
    # Identity hate
    "unna maadhiri aaluku idam illai",
    "un jaathikaaran thaan idhu seyvaanga",
    "madam pidi", "matha pidi",
    "terrorist payal", "jihadi payal",
    "desathrohi", "naatai vittu po",
]

mild_tl = [
    # Negative feelings
    "verupu", "verukkiren", "vera verupu",
    "kovam", "romba kovam", "kadichukkiren",
    "asingam", "asingamana", "mosam", "romba mosam",
    "bore adikuthu", "bore adichuduchu",
    "irritation", "irritation aguthu", "irritate panra",
    "aluppa", "soriyadha",
    # Dismissal
    "over aa pesadhae", "vaa mokkai", "scene podadhae",
    "yaaru kekka", "yaaru kekaradhu", "yarukku vendam",
    "shut up da", "vaaya moodunga",
    "thevaiyillaadhavan", "thevaiyilla",
    "romba over", "nallavendaam",
    "unna paathu sirikurom", "comedy figure",
    # Character attacks
    "poi solran", "poiyar", "avan poy solran",
    "nambikkai illaadhavan", "nambadhae",
    "fake figure", "fraud payal", "scam panra",
    "kaatikoduthavan", "throgai", "drohi",
    "clown maari", "paavam figure",
    "show off panra", "acting panra",
    "romba ahankaaram", "thamizhku throgam",
]

# ── HINDI (Devanagari script) ─────────────────────────────────────────────────
severe_hi = [
    # Kill / death threats
    "मार", "मारना", "मारूंगा", "मार डालूंगा", "मार दूंगा",
    "मार दो", "मार डालो", "मार दिया जाएगा",
    "हत्या", "हत्या करूंगा", "हत्या कर दूंगा", "हत्या करवाऊंगा",
    "क़त्ल", "क़त्ल करूंगा", "क़त्ल कर दूंगा",
    "मरवा दूंगा", "मरवा दो", "मरवा देंगे",
    "मर जाओ", "मर जा", "मरो", "मरना चाहिए तुम्हें",
    "जान से मारूंगा", "तुम्हें मार दूंगा", "तेरी जान लूंगा",
    "तुम्हारी जान लेकर रहूंगा", "खून कर दूंगा",
    "सिर काट दूंगा", "गला काट दूंगा", "टांग तोड़ दूंगा",
    # Sexual violence
    "बलात्कार", "रेप", "रेप करूंगा", "रेप कर दूंगा",
    "बलात्कार करूंगा", "छेड़छाड़",
    "यौन उत्पीड़न", "यौन हिंसा",
    # Weapons / explosives
    "बम", "बम फोड़ूंगा", "बम मार दूंगा",
    "विस्फोट", "विस्फोट करूंगा",
    "जला दूंगा", "जिंदा जला दूंगा", "आग लगा दूंगा",
    "गोली मार दूंगा", "गोली से उड़ा दूंगा",
    "चाकू मारूंगा", "छुरा घोंप दूंगा",
    "तेज़ाब फेंकूंगा", "एसिड अटैक",
    # Suicide incitement
    "आत्महत्या कर लो", "खुदकुशी कर लो",
    "नस काट लो", "जहर खा लो", "फांसी लगा लो",
    "ट्रेन के सामने कूद जाओ", "छत से कूद जाओ",
    "तुम्हारे बिना दुनिया बेहतर है",
    "तुम्हें कोई याद नहीं करेगा",
    "तुम्हारा परिवार खुश होगा तुम्हारे बिना",
    # Stalking / pursuit
    "धमकी", "धमकी दे रहा हूं",
    "तेरी खैर नहीं", "छोड़ूंगा नहीं", "देख लूंगा",
    "ढूंढ निकालूंगा", "तुम्हारा पता मुझे पता है",
    "नज़र रख रहा हूं", "पीछे पड़ा हूं",
]

hate_hi = [
    # Cognitive insults
    "मूर्ख", "मूर्ख कहीं का", "बेवकूफ", "बेवकूफ इंसान",
    "गधा", "गधे जैसा दिमाग", "उल्लू", "उल्लू के पट्ठे",
    "निकम्मा", "नालायक", "निकम्मे", "नालायक इंसान",
    "बुद्धू", "बुद्धू कहीं का", "पागल", "पागल है क्या",
    "दिमाग नहीं है", "अक्ल नहीं है", "जाहिल",
    # Animal comparisons
    "कुत्ता", "कुत्ते की औलाद", "कुत्ते जैसा",
    "सुअर", "सुअर जैसा", "सूअर",
    "जानवर", "जानवर की तरह",
    "गधा", "बंदर", "बंदर जैसा",
    "सांप", "चूहा", "कीड़ा",
    # Gendered / sexual slurs
    "कमीना", "कमीनी", "हरामी", "हरामजादा", "हरामजादी",
    "साला", "साली", "रंडी", "कुतिया", "छिनाल", "वेश्या",
    "नालायक औरत", "बेशर्म औरत",
    # General abuse
    "बकवास", "बकवास बंद करो", "बेशर्म", "बेहूदा",
    "घटिया", "घटिया इंसान", "घटिया सोच",
    "चुप रहो", "मुंह बंद करो", "भाग जाओ",
    "नरक में जाओ", "नरक में सड़ो",
    "तुम्हें कोई नहीं चाहता", "तुम्हें कोई पसंद नहीं करता",
    "गंदे इंसान", "गंदी सोच",
    # Identity hate
    "आतंकवादी", "देशद्रोही", "गद्दार", "दंगाई",
    "जातिवादी गाली", "नीची जात", "अछूत", "छोटी जात",
    "तुम्हारी जात ही ऐसी है",
    "तुम्हारे मजहब वाले सब ऐसे हैं",
    "अपने देश जाओ", "यहां से निकलो",
    "तुम्हारा यहां क्या काम",
]

mild_hi = [
    # Negative feelings
    "नफरत", "नफरत करता हूं", "नफरत है मुझे",
    "गुस्सा", "बहुत गुस्सा", "चिढ़", "चिढ़ है मुझे",
    "जलन", "ईर्ष्या", "कुढ़न",
    "परेशान", "बहुत परेशान", "तंग आ गया",
    # Negative descriptors
    "बेकार", "बेकार है", "बहुत बेकार",
    "बुरा", "बहुत बुरा", "बुरा लगा",
    "घटिया", "फालतू", "फालतू इंसान",
    "बकवास", "बकवास है", "बड़ी बकवास",
    "शर्मनाक", "बेइज्जती", "इज्जत नहीं",
    # Character attacks
    "झूठा", "झूठी", "झूठ बोलता है",
    "मक्कार", "धोखेबाज", "धोखेबाज इंसान",
    "पाखंडी", "नकली", "दिखावा करता है",
    "मतलबी", "स्वार्थी", "केवल मतलब से काम",
    "दोगला", "दोगलापन", "दो मुंह वाला",
    # Dismissal
    "बोरिंग", "थकाऊ", "उबाऊ",
    "ओवररेटेड", "इतना भी नहीं है", "झूठी शोहरत",
    "घमंडी", "अहंकारी", "बहुत घमंड",
    "चुप कर", "बकबक मत कर", "कोई नहीं सुनता",
    "किसी को फर्क नहीं पड़ता", "किसने पूछा",
    "रहने दो", "बेकार की बात",
]

# ═══════════════════════════════════════════════════════════════════════════════
# MERGE ALL TIERS
# ═══════════════════════════════════════════════════════════════════════════════
severe_words = severe_en + severe_ta + severe_tl + severe_hi
hate_words   = hate_en   + hate_ta   + hate_tl   + hate_hi
mild_words   = mild_en   + mild_ta   + mild_tl   + mild_hi


# ── Regex builder ─────────────────────────────────────────────────────────────
def make_pattern(words: list) -> re.Pattern:
    """
    Sort by length descending so longer phrases (e.g. 'kill yourself')
    match before their shorter substrings (e.g. 'kill').
    """
    sorted_words = sorted(words, key=len, reverse=True)
    escaped = [re.escape(w) for w in sorted_words]
    return re.compile(r'(?<!\w)(' + '|'.join(escaped) + r')(?!\w)', re.IGNORECASE)

severe_pat = make_pattern(severe_words)
hate_pat   = make_pattern(hate_words)
mild_pat   = make_pattern(mild_words)


# ── Labeling function ─────────────────────────────────────────────────────────
def auto_label(text: str) -> pd.Series:
    t = str(text)
    if severe_pat.search(t):
        return pd.Series({"label": "severe",      "severity": 3})
    elif hate_pat.search(t):
        return pd.Series({"label": "hate_speech", "severity": 2})
    elif mild_pat.search(t):
        return pd.Series({"label": "mild_toxic",  "severity": 1})
    else:
        return pd.Series({"label": "safe",         "severity": 0})


# ── Label ─────────────────────────────────────────────────────────────────────
print("Auto-labeling...")
df[["label", "severity"]] = df["text"].apply(auto_label)

print("\nAuto-label distribution:")
print(df["label"].value_counts())
print("\nSeverity distribution:")
print(df["severity"].value_counts().sort_index())

# ── Save ──────────────────────────────────────────────────────────────────────
df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
print(f"\nSaved {len(df)} rows → {OUTPUT_PATH}")