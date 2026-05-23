"""
Advanced SSML Generator with Google Cloud TTS best practices.
Implements transliteration, lang tags, phonemes, and prosody control.
"""

import re
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class AdvancedSSMLGenerator:
    """
    Advanced SSML generator following Google Cloud TTS best practices.
    
    Features:
    - Automatic transliteration (Roman Hindi → Devanagari)
    - <lang xml:lang="hi-IN"> tags for Hindi sections
    - <phoneme> support for pronunciation
    - Optimized prosody (rate 95%, pitch control)
    - Smart sentence segmentation
    """
    
    # Prosody settings (Optimized for NATURAL, HUMAN-LIKE speech)
    DEFAULT_RATE = "100%"     # Normal speed for most natural sound
    DEFAULT_PITCH = "-0.5st"  # Very slight lower for warmth
    
    # Pause durations
    PAUSES = {
        "short": "120ms",
        "medium": "160ms",
        "long": "200ms",
        "breath": "180ms",
    }
    
    
    # Import comprehensive Hindi vocabulary (700+ words)
    try:
        from agents.hindi_vocabulary_large import HINDI_TRANSLITERATION_MAP as TRANSLITERATION_MAP
    except ImportError:
        # Fallback to medium vocabulary
        try:
            from agents.hindi_vocabulary import HINDI_TRANSLITERATION_MAP as TRANSLITERATION_MAP
        except ImportError:
            # Final fallback to basic map
            TRANSLITERATION_MAP = {
                "main": "मैं", "mujhe": "मुझे", "aap": "आप",
                "hai": "है", "hain": "हैं", "hoon": "हूं",
                "achha": "अच्छा", "theek": "ठीक", "bahut": "बहुत",
            }
    
    @staticmethod
    def transliterate_word(word: str) -> str:
        """Simple transliteration for common Hindi words."""
        word_lower = word.lower()
        return AdvancedSSMLGenerator.TRANSLITERATION_MAP.get(word_lower, word)
    
    @staticmethod
    def transliterate_text(text: str, language: str) -> str:
        """
        Transliterate Roman Hindi to Devanagari for better pronunciation.
        Only for hindi/hinglish modes.
        """
        if language not in ['hindi', 'hinglish']:
            return text
        
        words = text.split()
        transliterated = []
        
        for word in words:
            # Keep punctuation
            punct = ""
            if word and word[-1] in '.!?,;:…':
                punct = word[-1]
                word = word[:-1]
            
            # Transliterate if in map
            trans_word = AdvancedSSMLGenerator.transliterate_word(word)
            transliterated.append(trans_word + punct)
        
        return ' '.join(transliterated)
    
    @staticmethod
    def wrap_hindi_sections(text: str, language: str) -> str:
        """
        Wrap Hindi/Hinglish text with <lang xml:lang="hi-IN"> tags.
        This tells Google TTS to use Hindi pronunciation rules.
        """
        if language not in ['hindi', 'hinglish']:
            return text
        
        # For now, wrap the entire text if it's Hindi/Hinglish
        # In production, you could detect and wrap only Hindi portions
        return f'<lang xml:lang="hi-IN">{text}</lang>'
    
    @staticmethod
    def add_smart_breaks(text: str) -> str:
        """
        Add MINIMAL breaks for natural speech flow.
        Too many breaks = robotic. Let TTS handle natural pauses.
        """
        # Only add breaks after sentences (very short)
        text = re.sub(r'([.!?।])\s+', r'\1 <break time="50ms"/> ', text)
        
        # Minimal pause after ellipsis
        text = re.sub(r'…\s*', r'… <break time="40ms"/> ', text)
        
        # NO breaks after commas - let TTS handle naturally
        # text = re.sub(r',\s+', r', <break time="30ms"/> ', text)
        
        return text
    
    @staticmethod
    def segment_long_sentences(text: str, max_length: int = 80) -> str:
        """
        Break long sentences to prevent unnatural prosody.
        Google TTS works better with shorter segments.
        """
        sentences = re.split(r'([.!?।]+)', text)
        
        result = []
        for i in range(0, len(sentences), 2):
            sentence = sentences[i].strip()
            punct = sentences[i+1] if i+1 < len(sentences) else ""
            
            if len(sentence) > max_length:
                # Break at conjunctions
                parts = re.split(r'\b(aur|lekin|par|toh|ki|kyunki)\b', sentence)
                for j, part in enumerate(parts):
                    if part.strip():
                        result.append(part.strip())
                        if j < len(parts) - 1:
                            result.append(' <break time="120ms"/> ')
                result.append(punct)
            else:
                result.append(sentence + punct)
        
        return ' '.join(result)
    
    @staticmethod
    def generate_advanced_ssml(
        text: str,
        language: Optional[str] = None,
        rate: Optional[str] = None,
        pitch: Optional[str] = None,
        use_transliteration: bool = True,
        use_lang_tags: bool = True
    ) -> str:
        """
        Generate advanced SSML following Google Cloud best practices.
        
        Args:
            text: Plain text to convert
            language: 'english' | 'hindi' | 'hinglish'
            rate: Speaking rate (default: 95%)
            pitch: Voice pitch (default: -1st)
            use_transliteration: Convert Roman Hindi → Devanagari
            use_lang_tags: Wrap Hindi with <lang> tags
            
        Returns:
            SSML markup string
        """
        # Detect language if not provided
        if language is None:
            # Try to use multilingual_utils, fallback to simple detection
            try:
                from agents.multilingual_utils import detect_language_mode
                language = detect_language_mode(text)
            except (ImportError, Exception):
                # Fallback: simple detection
                hindi_words = ['hai', 'hain', 'hoon', 'mujhe', 'aap', 'main']
                text_lower = text.lower()
                if any(word in text_lower for word in hindi_words):
                    language = 'hinglish'
                else:
                    language = 'english'
        
        # Use defaults
        rate = rate or AdvancedSSMLGenerator.DEFAULT_RATE
        pitch = pitch or AdvancedSSMLGenerator.DEFAULT_PITCH
        
        # Clean any existing SSML
        text = re.sub(r'<[^>]+>', '', text)
        
        # Step 1: Segment long sentences
        text = AdvancedSSMLGenerator.segment_long_sentences(text)
        
        # Step 2: Transliterate if enabled (Roman → Devanagari)
        if use_transliteration:
            text = AdvancedSSMLGenerator.transliterate_text(text, language)
            logger.info(f"Transliterated text for {language}")
        
        # Step 3: Add smart breaks
        text = AdvancedSSMLGenerator.add_smart_breaks(text)
        
        # Step 4: Wrap with lang tags if Hindi/Hinglish
        if use_lang_tags:
            text = AdvancedSSMLGenerator.wrap_hindi_sections(text, language)
        
        # Step 5: Build final SSML
        ssml = f"""<speak>
  <prosody rate="{rate}" pitch="{pitch}">
    <break time="120ms"/>
    {text}
    <break time="180ms"/>
  </prosody>
</speak>"""
        
        logger.debug(f"Generated advanced SSML for {language}: {len(ssml)} chars")
        
        return ssml


# Convenience function
def generate_advanced_ssml(text: str, language: Optional[str] = None, **kwargs) -> str:
    """Generate advanced SSML with Google Cloud best practices."""
    return AdvancedSSMLGenerator.generate_advanced_ssml(text, language, **kwargs)
