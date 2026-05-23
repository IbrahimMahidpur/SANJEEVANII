"""
Comprehensive Hindi Transliteration Dictionary
Roman Hindi → Devanagari mapping for natural TTS pronunciation
"""

# Core vocabulary - Most common Hindi words
CORE_VOCABULARY = {
    # Pronouns
    "main": "मैं", "mujhe": "मुझे", "mera": "मेरा", "meri": "मेरी", "mere": "मेरे",
    "aap": "आप", "aapka": "आपका", "aapki": "आपकी", "aapke": "आपके",
    "tum": "तुम", "tumhara": "तुम्हारा", "tumhari": "तुम्हारी", "tumhare": "तुम्हारे",
    "yeh": "यह", "woh": "वह", "ye": "ये", "wo": "वो",
    "koi": "कोई", "kuch": "कुछ", "sab": "सब", "sabhi": "सभी",
    
    # Verbs - Present
    "hai": "है", "hain": "हैं", "hoon": "हूं", "ho": "हो",
    "tha": "था", "thi": "थी", "the": "थे", "theen": "थीं",
    "hoga": "होगा", "hogi": "होगी", "honge": "होंगे", "hongi": "होंगी",
    
    # Verbs - Common actions
    "kar": "कर", "karna": "करना", "karta": "करता", "karti": "करती", "karte": "करते",
    "kar": "कर", "karo": "करो", "kare": "करें", "kariye": "करिए",
    "raha": "रहा", "rahi": "रही", "rahe": "रहे", "rahi": "रही",
    "ja": "जा", "jana": "जाना", "jata": "जाता", "jati": "जाती", "jate": "जाते",
    "aa": "आ", "aana": "आना", "aata": "आता", "aati": "आती", "aate": "आते",
    "de": "दे", "dena": "देना", "deta": "देता", "deti": "देती", "dete": "देते",
    "le": "ले", "lena": "लेना", "leta": "लेता", "leti": "लेती", "lete": "लेते",
    "bol": "बोल", "bolna": "बोलना", "bolta": "बोलता", "bolti": "बोलती",
    "sun": "सुन", "sunna": "सुनना", "sunta": "सुनता", "sunti": "सुनती",
    "dekh": "देख", "dekhna": "देखना", "dekhta": "देखता", "dekhti": "देखती",
    "samajh": "समझ", "samajhna": "समझना", "samajhta": "समझता", "samajhti": "समझती",
    "soch": "सोच", "sochna": "सोचना", "sochta": "सोचता", "sochti": "सोचती",
    "baat": "बात", "batana": "बताना", "batata": "बताता", "batati": "बताती",
    "pata": "पता", "puchna": "पूछना", "puchta": "पूछता", "puchti": "पूछती",
    
    # Modal verbs
    "sakta": "सकता", "sakti": "सकती", "sakte": "सकते", "sakti": "सकती",
    "chahiye": "चाहिए", "chahta": "चाहता", "chahti": "चाहती", "chahte": "चाहते",
    "padta": "पड़ता", "padti": "पड़ती", "padte": "पड़ते", "padti": "पड़ती",
    
    # Adjectives - Emotions & States
    "achha": "अच्छा", "achhi": "अच्छी", "achhe": "अच्छे",
    "bura": "बुरा", "buri": "बुरी", "bure": "बुरे",
    "theek": "ठीक", "sahi": "सही", "galat": "गलत",
    "khush": "खुश", "udaas": "उदास", "pareshan": "परेशान",
    "dukhi": "दुखी", "sukhi": "सुखी", "shant": "शांत",
    "gussa": "गुस्सा", "dar": "डर", "pyar": "प्यार",
    "chinta": "चिंता", "tension": "टेंशन", "stress": "स्ट्रेस",
    "anxiety": "एंग्जायटी", "depression": "डिप्रेशन",
    
    # Adjectives - Descriptive
    "bada": "बड़ा", "badi": "बड़ी", "bade": "बड़े",
    "chhota": "छोटा", "chhoti": "छोटी", "chhote": "छोटे",
    "lamba": "लंबा", "lambi": "लंबी", "lambe": "लंबे",
    "naya": "नया", "nayi": "नई", "naye": "नए",
    "purana": "पुराना", "purani": "पुरानी", "purane": "पुराने",
    "bahut": "बहुत", "zyada": "ज़्यादा", "kam": "कम",
    "thoda": "थोड़ा", "thodi": "थोड़ी", "thode": "थोड़े",
    
    # Conjunctions & Connectors
    "aur": "और", "ya": "या", "lekin": "लेकिन", "par": "पर",
    "ki": "कि", "ke": "के", "ka": "का", "ki": "की",
    "toh": "तो", "to": "तो", "kyunki": "क्योंकि", "isliye": "इसलिए",
    "agar": "अगर", "jab": "जब", "tab": "तब", "phir": "फिर",
    
    # Question words
    "kya": "क्या", "kaun": "कौन", "kab": "कब", "kahan": "कहां",
    "kaise": "कैसे", "kyun": "क्यों", "kitna": "कितना", "kitni": "कितनी",
    
    # Negation
    "nahi": "नहीं", "na": "ना", "mat": "मत", "bilkul": "बिल्कुल",
    
    # Adverbs
    "abhi": "अभी", "ab": "अब", "kal": "कल", "aaj": "आज",
    "hamesha": "हमेशा", "kabhi": "कभी", "jaldi": "जल्दी", "der": "देर",
    "yahan": "यहां", "wahan": "वहां", "idhar": "इधर", "udhar": "उधर",
    "andar": "अंदर", "bahar": "बाहर", "upar": "ऊपर", "neeche": "नीचे",
    
    # Common nouns
    "ghar": "घर", "kaam": "काम", "din": "दिन", "raat": "रात",
    "subah": "सुबह", "shaam": "शाम", "dopahar": "दोपहर",
    "paani": "पानी", "khana": "खाना", "log": "लोग", "dost": "दोस्त",
    "parivaar": "परिवार", "maa": "मां", "baap": "बाप", "beta": "बेटा",
    "beti": "बेटी", "bhai": "भाई", "behen": "बहन",
    
    # Therapy-specific terms
    "dukh": "दुख", "sukh": "सुख", "dard": "दर्द", "takleef": "तकलीफ",
    "musibat": "मुसीबत", "pareshani": "परेशानी", "samasya": "समस्या",
    "hal": "हल", "upay": "उपाय", "tarika": "तरीका", "raasta": "रास्ता",
    "madad": "मदद", "sahayata": "सहायता", "support": "सपोर्ट",
    "vishwas": "विश्वास", "bharosa": "भरोसा", "ummeed": "उम्मीद",
    "himmat": "हिम्मत", "hausla": "हौसला", "shakti": "शक्ति",
    
    # Feelings & Emotions (Extended)
    "feel": "फील", "feeling": "फीलिंग", "emotion": "इमोशन",
    "khushi": "खुशी", "gam": "गम", "dukh": "दुख",
    "gussa": "गुस्सा", "krodh": "क्रोध", "nafrat": "नफरत",
    "mohabbat": "मोहब्बत", "ishq": "इश्क", "prem": "प्रेम",
    "dar": "डर", "bhay": "भय", "ghabrahat": "घबराहट",
    "sharam": "शर्म", "lajja": "लज्जा", "sharminda": "शर्मिंदा",
    
    # Common phrases
    "koi": "कोई", "baat": "बात", "nahi": "नहीं",
    "theek": "ठीक", "hai": "है", "okay": "ओके",
    "haan": "हां", "ji": "जी", "nahin": "नहीं",
    "please": "प्लीज", "sorry": "सॉरी", "thanks": "थैंक्स",
    "welcome": "वेलकम", "bye": "बाय", "hello": "हेलो",
    
    # Medical/Health terms
    "sehat": "सेहत", "bimari": "बीमारी", "dawai": "दवाई",
    "doctor": "डॉक्टर", "hospital": "हॉस्पिटल", "clinic": "क्लिनिक",
    "treatment": "ट्रीटमेंट", "ilaj": "इलाज", "upchar": "उपचार",
    
    # CBT-specific
    "soch": "सोच", "vichar": "विचार", "thought": "थॉट",
    "behavior": "बिहेवियर", "vyavhar": "व्यवहार",
    "pattern": "पैटर्न", "habit": "हैबिट", "aadat": "आदत",
    "change": "चेंज", "badlav": "बदलाव", "sudhar": "सुधार",
    
    # Numbers
    "ek": "एक", "do": "दो", "teen": "तीन", "char": "चार", "paanch": "पांच",
    "chhe": "छह", "saat": "सात", "aath": "आठ", "nau": "नौ", "das": "दस",
    
    # Common English words in Hinglish
    "problem": "प्रॉब्लम", "issue": "इश्यू", "matter": "मैटर",
    "situation": "सिचुएशन", "condition": "कंडीशन",
    "normal": "नॉर्मल", "common": "कॉमन", "natural": "नेचुरल",
    "important": "इंपॉर्टेंट", "zaruri": "ज़रूरी", "zaroori": "ज़रूरी",
    "difficult": "डिफिकल्ट", "mushkil": "मुश्किल", "kathin": "कठिन",
    "easy": "ईज़ी", "aasan": "आसान", "simple": "सिंपल",
    "better": "बेटर", "worse": "वर्स", "same": "सेम",
    "different": "डिफरेंट", "alag": "अलग", "similar": "सिमिलर",
}

# Extended vocabulary - Additional common words
EXTENDED_VOCABULARY = {
    # More verbs
    "milna": "मिलना", "milta": "मिलता", "milti": "मिलती",
    "hona": "होना", "hota": "होता", "hoti": "होती",
    "khana": "खाना", "khata": "खाता", "khati": "खाती",
    "peena": "पीना", "peeta": "पीता", "peeti": "पीती",
    "sona": "सोना", "sota": "सोता", "soti": "सोती",
    "uthna": "उठना", "uthta": "उठता", "uthti": "उठती",
    "baithna": "बैठना", "baithta": "बैठता", "baithti": "बैठती",
    "khada": "खड़ा", "khadi": "खड़ी", "khade": "खड़े",
    "chalna": "चलना", "chalta": "चलता", "chalti": "चलती",
    "bhagna": "भागना", "bhagta": "भागता", "bhagti": "भागती",
    "likhna": "लिखना", "likhta": "लिखता", "likhti": "लिखती",
    "padhna": "पढ़ना", "padhta": "पढ़ता", "padhti": "पढ़ती",
    
    # More emotions
    "khushi": "खुशी", "gham": "गम", "dukh": "दुख",
    "santosh": "संतोष", "asantosh": "असंतोष",
    "shanti": "शांति", "ashanti": "अशांति",
    "asha": "आशा", "nirasha": "निराशा",
    "bharosa": "भरोसा", "vishwas": "विश्वास",
    "shak": "शक", "sandeh": "संदेह", "doubt": "डाउट",
    
    # Time expressions
    "parso": "परसों", "tarso": "तरसों",
    "mahina": "महीना", "saal": "साल", "varsh": "वर्ष",
    "ghanta": "घंटा", "minute": "मिनट", "second": "सेकंड",
    "samay": "समय", "waqt": "वक्त", "time": "टाइम",
    
    # Places
    "jagah": "जगह", "sthan": "स्थान", "place": "प्लेस",
    "sheher": "शहर", "gaon": "गांव", "village": "विलेज",
    "desh": "देश", "country": "कंट्री", "videsh": "विदेश",
    "office": "ऑफिस", "school": "स्कूल", "college": "कॉलेज",
    
    # More common words
    "zarurat": "ज़रूरत", "need": "नीड", "chahiye": "चाहिए",
    "mangna": "मांगना", "demand": "डिमांड",
    "dena": "देना", "give": "गिव", "lena": "लेना", "take": "टेक",
    "banana": "बनाना", "make": "मेक", "todna": "तोड़ना", "break": "ब्रेक",
}

# Combine all vocabularies
HINDI_TRANSLITERATION_MAP = {**CORE_VOCABULARY, **EXTENDED_VOCABULARY}

# Total words
print(f"Total Hindi words in library: {len(HINDI_TRANSLITERATION_MAP)}")
