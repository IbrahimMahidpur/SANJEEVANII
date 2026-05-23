"""
Enhanced Language Detection for Hindi, English, and Hinglish.

This module provides sophisticated language detection specifically optimized
for Indian languages and code-mixed speech (Hinglish).
"""

import re
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class LanguageDetector:
    """
    Advanced language detector for Hindi, English, and Hinglish.
    
    Uses multiple signals:
    - Unicode script detection (Devanagari vs Latin)
    - Common Hindi words and patterns
    - English vocabulary patterns
    - Code-mixing indicators
    """
    
    # Common Hindi words (in both Devanagari and transliteration)
    # EXPANDED: More coverage for better detection
    HINDI_WORDS = {
        # Devanagari - Basic
        'है', 'हैं', 'था', 'थी', 'थे', 'हूं', 'हूँ', 'हो', 'मैं', 'तुम', 'आप', 'हम',
        'क्या', 'कैसे', 'कहाँ', 'कहां', 'कब', 'क्यों', 'और', 'या', 'का', 'के', 'की', 'को',
        'मेरा', 'मेरी', 'मेरे', 'तुम्हारा', 'तुम्हारी', 'उसका', 'उसकी', 'इसका', 'यह', 'वह', 'ये', 'वो',
        'चाहिए', 'चाहता', 'चाहती', 'सकता', 'सकती', 'सकते', 'करना', 'होना', 'जाना',
        'देना', 'लेना', 'जाना', 'आना', 'बोलना', 'समझ', 'समझा', 'बता', 'बताओ', 'दो', 'दे',
        'नहीं', 'ना', 'हाँ', 'जी', 'अच्छा', 'ठीक', 'कर', 'करो', 'करें', 'कैसा', 'कैसी',
        'सुनो', 'देखो', 'देख', 'पता', 'मतलब', 'वाला', 'वाली', 'गया', 'गयी', 'गए',
        'अभी', 'फिर', 'तो', 'भी', 'बस', 'बहुत', 'कुछ', 'सब', 'कोई', 'कौन',
        'जरूर', 'शायद', 'पर', 'लेकिन', 'मगर', 'इसलिए', 'क्योंकि', 'ताकि',
        
        # Common transliterations (phonetic)
        'hai', 'hain', 'tha', 'thi', 'the', 'hoon', 'ho', 'main', 'tum', 'aap', 'hum',
        'kya', 'kaise', 'kahan', 'kab', 'kyun', 'kyu', 'aur', 'ya', 'ka', 'ke', 'ki', 'ko',
        'mera', 'meri', 'mere', 'tumhara', 'tumhari', 'uska', 'uski', 'iska', 'yeh', 'ye', 'vah', 'vo', 'woh',
        'chahiye', 'chahie', 'chahta', 'chahti', 'chahte', 'sakta', 'sakti', 'sakte', 'karna', 'hona',
        'dena', 'lena', 'jana', 'aana', 'bolna', 'samajh', 'samjha', 'bata', 'batao', 'btao', 'do', 'de',
        'nahi', 'nhi', 'na', 'han', 'haan', 'ji', 'acha', 'achha', 'theek', 'thik', 'kar', 'karo', 'kare',
        'suno', 'dekho', 'dekh', 'pata', 'matlab', 'mtlb', 'wala', 'wali', 'gaya', 'gayi', 'gaye',
        'abhi', 'phir', 'fir', 'to', 'toh', 'bhi', 'bas', 'bahut', 'bhut', 'kuch', 'kch', 'sab', 'koi', 'kaun', 'kon',
        'zaroor', 'jarur', 'shayad', 'par', 'lekin', 'magar', 'isliye', 'kyunki', 'kyonki', 'taaki',
        
        # Common Hinglish particles
        'bhi', 'toh', 'yaar', 'yr', 'bhai', 'dude', 'bro', 'na', 'naa', 're',
        'arrey', 'arre', 'accha', 'achha', 'oho', 'haan', 'hmm', 'theek',
        
        # Common verbs in transliteration
        'ho', 'hai', 'hain', 'hua', 'hui', 'hue', 'hoga', 'hogi', 'honge',
        'kar', 'karo', 'karna', 'kiya', 'kiye', 'karunga', 'karenge',
        'de', 'do', 'dena', 'diya', 'diye', 'dunga', 'denge',
        'le', 'lo', 'lena', 'liya', 'liye', 'lunga', 'lenge',
        'ja', 'jao', 'jana', 'gaya', 'gaye', 'jaunga', 'jayenge',
        'aa', 'aao', 'aana', 'aaya', 'aaye', 'aaunga', 'aayenge',
        
        # Questions/Interrogatives
        'kya', 'kaise', 'kaha', 'kahan', 'kab', 'kyun', 'kyu', 'kaun', 'kon',
        'kaunsa', 'konsa', 'kitna', 'kitne', 'kitni', 'kis', 'kiska', 'kiske',
        
        # Common Hindi/Hinglish expressions
        'theek', 'thik', 'sahi', 'galat', 'achha', 'acha', 'bura', 'kharab',
        'badhiya', 'mast', 'suna', 'dekha', 'pata', 'samjha', 'mila'
    }
    
    # Common Hinglish patterns
    HINGLISH_PATTERNS = [
        r'\b(kar|ho|hai|hoon|chahiye|sakta|sakti)\b.*\b(is|are|was|were|can|will|should)\b',
        r'\b(is|are|was|were|can|will|should)\b.*\b(kar|ho|hai|hoon|chahiye|sakta|sakti)\b',
        r'\b(mujhe|tumhe|usko)\b.*\b(help|problem|question|issue)\b',
        r'\b(help|please|thanks|sorry)\b.*\b(chahiye|do|karo|batao)\b',
    ]
    
    # English stop words (common words)
    ENGLISH_STOPWORDS = {
        'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'should', 'could', 'can', 'may', 'might', 'must',
        'i', 'you', 'he', 'she', 'it', 'we', 'they',
        'my', 'your', 'his', 'her', 'its', 'our', 'their',
        'this', 'that', 'these', 'those', 'what', 'which', 'who',
        'when', 'where', 'why', 'how', 'please', 'thanks', 'hello'
    }
    
    @staticmethod
    def has_devanagari(text: str) -> bool:
        """Check if text contains Devanagari script."""
        return any('\u0900' <= c <= '\u097F' for c in text)
    
    @staticmethod
    def has_bengali(text: str) -> bool:
        """Check if text contains Bengali script."""
        return any('\u0980' <= c <= '\u09FF' for c in text)
    
    @staticmethod
    def count_hindi_words(text: str) -> int:
        """Count Hindi words in text (both Devanagari and transliteration)."""
        words = set(text.lower().split())
        return len(words & LanguageDetector.HINDI_WORDS)
    
    @staticmethod
    def count_english_words(text: str) -> int:
        """Count English words in text."""
        words = set(re.findall(r'\b[a-zA-Z]+\b', text.lower()))
        return len(words & LanguageDetector.ENGLISH_STOPWORDS)
    
    @staticmethod
    def is_hinglish(text: str) -> bool:
        """Detect if text is Hinglish (code-mixed)."""
        # Check for Hinglish patterns
        for pattern in LanguageDetector.HINGLISH_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        # Check if text has both Hindi and English words
        hindi_count = LanguageDetector.count_hindi_words(text)
        english_count = LanguageDetector.count_english_words(text)
        
        # If both languages present, it's Hinglish
        return hindi_count > 0 and english_count > 0
    
    @staticmethod
    def detect_language(text: str, detailed: bool = False) -> Tuple[str, Optional[dict]]:
        """
        Detect language of text.
        
        Args:
            text: Input text to analyze
            detailed: If True, return detailed analysis
            
        Returns:
            Tuple of (language_code, optional_details)
            language_code: "hi-IN", "en-IN", "en-US", or "hinglish"
            details: Dictionary with detection metrics (if detailed=True)
        """
        if not text or not text.strip():
            return ("en-IN", None)
        
        # Normalize text
        text_normalized = text.strip()
        
        # Check for Devanagari script (definitive Hindi)
        if LanguageDetector.has_devanagari(text_normalized):
            logger.info(f"Detected Devanagari script → hi-IN")
            details = {"script": "devanagari", "confidence": 1.0} if detailed else None
            return ("hi-IN", details)
        
        # Check for Bengali script
        if LanguageDetector.has_bengali(text_normalized):
            logger.info(f"Detected Bengali script → bn-IN")
            details = {"script": "bengali", "confidence": 1.0} if detailed else None
            return ("bn-IN", details)
        
        # Count language-specific words
        hindi_count = LanguageDetector.count_hindi_words(text_normalized)
        english_count = LanguageDetector.count_english_words(text_normalized)
        total_words = len(text_normalized.split())
        
        # Check for Hinglish
        is_hinglish = LanguageDetector.is_hinglish(text_normalized)
        
        if is_hinglish:
            logger.info(f"Detected code-mixing → Hinglish (Hindi: {hindi_count}, English: {english_count})")
            details = {
                "type": "code-mixed",
                "hindi_words": hindi_count,
                "english_words": english_count,
                "total_words": total_words
            } if detailed else None
            # For Hinglish, prefer Indian English voice
            return ("en-IN", details)
        
        # Determine dominant language
        if hindi_count > english_count:
            logger.info(f"Detected Hindi (transliterated) → hi-IN (Hindi: {hindi_count}, English: {english_count})")
            details = {
                "type": "transliterated_hindi",
                "hindi_words": hindi_count,
                "english_words": english_count,
                "confidence": hindi_count / max(total_words, 1)
            } if detailed else None
            return ("hi-IN", details)
        
        elif english_count > 0:
            logger.info(f"Detected English → en-IN (Hindi: {hindi_count}, English: {english_count})")
            details = {
                "type": "english",
                "hindi_words": hindi_count,
                "english_words": english_count,
                "confidence": english_count / max(total_words, 1)
            } if detailed else None
            return ("en-IN", details)
        
        # Default to Indian English
        logger.info(f"Default detection → en-IN")
        details = {"type": "default", "total_words": total_words} if detailed else None
        return ("en-IN", details)
    
    @staticmethod
    def get_optimal_tts_language(detected_lang: str, text: str) -> str:
        """
        Get optimal TTS language code based on detection and text content.
        
        For Hinglish, we need to be smart:
        - If mostly Hindi words → use Hindi voice
        - If mostly English words → use Indian English voice
        - If mixed → use Indian English (better for code-mixing)
        
        Args:
            detected_lang: Language code from STT or detection
            text: The actual text to synthesize
            
        Returns:
            Optimal language code for TTS
        """
        # If Devanagari script present, always use Hindi
        if LanguageDetector.has_devanagari(text):
            return "hi-IN"
        
        # For detected Hindi, check if transliteration or script
        if detected_lang.upper() in ["HI-IN", "HI"]:
            return "hi-IN"
        
        # For detected English or Hinglish, analyze text
        hindi_count = LanguageDetector.count_hindi_words(text)
        english_count = LanguageDetector.count_english_words(text)
        
        # If Hindi dominates, use Hindi voice even for transliteration
        if hindi_count > english_count * 1.5:
            return "hi-IN"
        
        # Otherwise use Indian English (handles Hinglish well)
        return "en-IN"
