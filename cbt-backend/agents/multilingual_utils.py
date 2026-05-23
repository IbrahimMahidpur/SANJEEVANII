"""
Enhanced utilities for multilingual processing, especially Hinglish.
Adapted from Sanjeevani module for CBT therapy context.

Provides text polishing, language detection, and pronunciation improvements
for Hindi, English, and Hinglish (code-mixed) text.
"""

import re
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


# Common Hinglish word mapping for better TTS pronunciation
HINGLISH_PRONUNCIATION_MAP = {
    # Common transliteration corrections
    "kaise": "कैसे",
    "kya": "क्या",
    "hai": "है",
    "hain": "हैं",
    "hoon": "हूं",
    "nahi": "नहीं",
    "nahin": "नहीं",
    "achha": "अच्छा",
    "acha": "अच्छा",
    "theek": "ठीक",
    "thik": "ठीक",
    "chahiye": "चाहिए",
    "chahie": "चाहिए",
    "batao": "बताओ",
    "bataye": "बताए",
    "samajh": "समझ",
    "samjhe": "समझे",
    "karo": "करो",
    "karen": "करें",
    "main": "मैं",
    "mujhe": "मुझे",
    "tumhe": "तुम्हें",
    "kyun": "क्यों",
    "kyu": "क्यों",
    "kahan": "कहाँ",
    "kab": "कब",
    "abhi": "अभी",
    "jaldi": "जल्दी",
    "dhyan": "ध्यान",
    "zaroor": "ज़रूर",
    "zarur": "ज़रूर",
    "shayad": "शायद",
    "bilkul": "बिल्कुल",
}


# Common Hindi words for detection
HINDI_WORDS = {
    'hai', 'hain', 'tha', 'thi', 'hoon', 'main', 'tum', 'aap', 'hum',
    'kya', 'kaise', 'kahan', 'kab', 'kyun', 'kyu', 'aur', 'mera', 'meri', 'mere',
    'chahiye', 'chahie', 'chahta', 'chahti', 'sakta', 'sakti', 'sakte',
    'nahi', 'nhi', 'haan', 'acha', 'achha', 'theek', 'thik', 'karo', 'kare',
    'suno', 'dekho', 'pata', 'matlab', 'mtlb', 'wala', 'wali',
    'abhi', 'phir', 'fir', 'toh', 'bhi', 'bahut', 'bhut', 'kuch', 'sab', 'koi',
    'zaroor', 'jarur', 'shayad', 'lekin', 'magar', 'isliye', 'kyunki', 'taaki',
    'yaar', 'bhai', 'arrey', 'arre',
}


def detect_language_mode(text: str) -> str:
    """
    Detect if text is English, Hindi, or Hinglish.
    
    Args:
        text: Input text to analyze
        
    Returns:
        "hindi", "english", or "hinglish"
    """
    # Check for Devanagari script
    has_devanagari = any('\u0900' <= c <= '\u097F' for c in text)
    
    if has_devanagari:
        # Check if mixed with English
        has_english = bool(re.search(r'[a-zA-Z]{3,}', text))
        return "hinglish" if has_english else "hindi"
    
    # Check for Hindi words in transliteration
    words = set(text.lower().split())
    hindi_words = words & HINDI_WORDS
    
    # Check for English words
    english_words = words - hindi_words
    
    if hindi_words and english_words:
        return "hinglish"
    elif hindi_words:
        return "hindi"
    else:
        return "english"


def polish_hinglish(text: str, target_tts_lang: str = None) -> str:
    """
    Polish Hinglish text for better TTS pronunciation.
    
    Strategy:
    - If target is hi-IN: Convert common transliterated words to Devanagari
    - If target is en-IN: Keep as-is but clean formatting
    
    Args:
        text: Input text (possibly Hinglish)
        target_tts_lang: Target TTS language ("hi-IN", "en-IN", etc.)
        
    Returns:
        Polished text optimized for TTS
    """
    if not text or not text.strip():
        return text
    
    # Detect language mode
    mode = detect_language_mode(text)
    logger.info(f"Language mode: {mode}, Target TTS: {target_tts_lang}")
    
    # If already pure Devanagari, return as-is
    if mode == "hindi" and any('\u0900' <= c <= '\u097F' for c in text):
        return text
    
    # If target is Hindi TTS and we have transliterated Hindi, convert key words
    if target_tts_lang and target_tts_lang.lower().startswith('hi') and mode in ["hindi", "hinglish"]:
        # Convert transliterated Hindi words to Devanagari for better pronunciation
        polished = text
        for eng_word, hindi_word in HINGLISH_PRONUNCIATION_MAP.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(eng_word) + r'\b'
            polished = re.sub(pattern, hindi_word, polished, flags=re.IGNORECASE)
        
        logger.debug(f"Polished for Hindi TTS: '{text}' → '{polished}'")
        return polished
    
    # For English TTS or pure English, return cleaned text
    return text


def add_hinglish_pauses(text: str) -> str:
    """
    Add natural pauses (commas) for better Hinglish TTS flow.
    
    Args:
        text: Input text
        
    Returns:
        Text with added pauses
    """
    # Add pause after common Hindi transition words if not already present
    transition_words = ['aur', 'और', 'lekin', 'लेकिन', 'phir', 'फिर', 'to', 'toh', 'तो', 'par', 'पर', 'kyunki', 'क्योंकि']
    
    for word in transition_words:
        # Add comma after transition word if not already there
        pattern = r'\b' + re.escape(word) + r'\b(?!\s*[,.])'
        text = re.sub(pattern, word + ',', text, flags=re.IGNORECASE)
    
    return text


def normalize_hinglish_numbers(text: str) -> str:
    """
    Normalize number formats for better Hinglish TTS.
    
    Converts:
    - "10 lakh" → "10,00,000" (Indian format)
    - "5 crore" → "5,00,00,000"
    
    Args:
        text: Input text with numbers
        
    Returns:
        Text with normalized numbers
    """
    # Convert "X lakh" to Indian format
    text = re.sub(
        r'(\d+(?:\.\d+)?)\s*(?:lakh|lakhs)',
        lambda m: f"{float(m.group(1)) * 100000:,.0f}",
        text,
        flags=re.IGNORECASE
    )
    
    # Convert "X crore" to Indian format
    text = re.sub(
        r'(\d+(?:\.\d+)?)\s*(?:crore|crores)',
        lambda m: f"{float(m.group(1)) * 10000000:,.0f}",
        text,
        flags=re.IGNORECASE
    )
    
    return text


def enhance_text_for_tts(text: str, detected_language: str = None) -> Tuple[str, str]:
    """
    Comprehensive text enhancement for TTS.
    
    Combines multiple enhancement strategies:
    - Markdown removal
    - Language-specific polishing
    - Pause insertion
    - Number normalization
    
    Args:
        text: Input text
        detected_language: Detected language code ("hi-IN", "en-IN", etc.)
        
    Returns:
        Tuple of (enhanced_text, optimal_tts_language)
    """
    if not text or not text.strip():
        return text, detected_language or "en-IN"
    
    # Remove markdown formatting
    enhanced = text
    enhanced = re.sub(r'\*\*(.+?)\*\*', r'\1', enhanced)  # Bold
    enhanced = re.sub(r'\*(.+?)\*', r'\1', enhanced)  # Italic
    enhanced = re.sub(r'__(.+?)__', r'\1', enhanced)  # Underline
    enhanced = re.sub(r'_(.+?)_', r'\1', enhanced)  # Italic
    enhanced = re.sub(r'^#{1,6}\s+', '', enhanced, flags=re.MULTILINE)  # Headers
    enhanced = re.sub(r'^\s*[\*\-\d+\.]\s+', '', enhanced, flags=re.MULTILINE)  # Lists
    
    # Detect language mode
    mode = detect_language_mode(enhanced)
    
    # Determine optimal TTS language
    optimal_lang = "en-IN"  # Default
    if mode == "hindi":
        optimal_lang = "hi-IN"
    elif mode == "hinglish":
        # For Hinglish, prefer Indian English voice (handles code-mixing better)
        optimal_lang = "en-IN"
    
    logger.info(f"Optimal TTS language: {optimal_lang} for mode: {mode}")
    
    # Polish for specific language
    enhanced = polish_hinglish(enhanced, optimal_lang)
    
    # Add natural pauses
    enhanced = add_hinglish_pauses(enhanced)
    
    # Normalize numbers
    enhanced = normalize_hinglish_numbers(enhanced)
    
    # Clean up extra whitespace
    enhanced = re.sub(r'\s+', ' ', enhanced).strip()
    
    return enhanced, optimal_lang
