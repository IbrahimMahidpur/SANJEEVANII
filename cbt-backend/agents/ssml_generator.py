"""
SSML Generator - Creates realistic, natural-sounding SSML for Google Cloud TTS.
Adapted from Sanjeevani module for CBT therapy context.

This module generates SSML markup with:
- Natural pauses and breathing sounds
- Emotional prosody (rate, pitch)
- Language-specific templates
- Automatic language detection
- Emphasis on important medical/therapy terms
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class SSMLGenerator:
    """
    Generate SSML markup for realistic, natural-sounding speech.
    
    Supports automatic language detection and applies appropriate
    prosody, pauses, and emotional elements for each language.
    """
    
    # Prosody configuration for natural, caring voice (Google Cloud optimized)
    DEFAULT_RATE = "95%"      # Google Cloud recommended
    DEFAULT_PITCH = "-1st"    # Google Cloud recommended
    
    # Language-specific intros (natural hesitations/fillers)
    LANGUAGE_INTROS = {
        "hinglish": "Achha…",
        "hindi": "Dekhiye…",
        "english": "Alright…",
    }
    
    # Pause durations (in milliseconds) - Sanjeevani-optimized
    PAUSES = {
        "short": "120ms",      # Short hesitation
        "medium": "250ms",     # Between clauses
        "long": "400ms",       # Sentence pause / breath
        "breath": "340ms",     # Breathing pause
    }
    
    @staticmethod
    def detect_language_from_text(text: str) -> str:
        """
        Simple language detection from text content.
        
        Args:
            text: Input text to analyze
            
        Returns:
            'english' | 'hindi' | 'hinglish'
        """
        try:
            from agents.multilingual_utils import detect_language_mode
            return detect_language_mode(text)
        except ImportError:
            # Fallback to simple detection
            hindi_keywords = ['hai', 'hoon', 'aap', 'kya', 'kaise', 'mujhe', 'chahiye']
            english_keywords = ['is', 'are', 'the', 'what', 'how', 'should', 'can']
            
            text_lower = text.lower()
            hindi_count = sum(1 for word in hindi_keywords if word in text_lower)
            english_count = sum(1 for word in english_keywords if word in text_lower)
            
            if hindi_count > english_count * 2:
                return 'hindi'
            elif english_count > hindi_count * 2:
                return 'english'
            else:
                return 'hinglish'
    
    @staticmethod
    def add_natural_pauses(text: str) -> str:
        """
        Add natural pauses to text for better rhythm.
        
        Args:
            text: Input text
            
        Returns:
            Text with SSML pause tags
        """
        # Add pauses after sentences
        text = re.sub(r'([.!?।])\s+', r'\1 <break time="400ms"/> ', text)
        
        # Add pauses after commas
        text = re.sub(r',\s+', r', <break time="250ms"/> ', text)
        
        # Add pauses after ellipsis
        text = re.sub(r'…\s*', r'… <break time="300ms"/> ', text)
        
        return text
    
    @staticmethod
    def add_emphasis(text: str) -> str:
        """
        Add emphasis to important CBT/therapy terms.
        
        Args:
            text: Input text
            
        Returns:
            Text with SSML emphasis tags
        """
        # Emphasize important therapy/medical terms
        important_words = [
            # English
            'immediately', 'urgent', 'emergency', 'doctor', 'hospital', 'crisis',
            'important', 'critical', 'serious', 'help', 'support',
            # Hindi/Hinglish
            'turant', 'zaruri', 'doctor', 'hospital', 'madad', 'sahayata',
            'zaroor', 'bahut', 'important'
        ]
        
        for word in important_words:
            # Use word boundaries to avoid partial matches
            pattern = r'\b(' + re.escape(word) + r')\b'
            replacement = r'<emphasis level="moderate">\1</emphasis>'
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    @staticmethod
    def generate_ssml(
        text: str,
        language: Optional[str] = None,
        rate: Optional[str] = None,
        pitch: Optional[str] = None,
        add_breath: bool = True,
        add_intro: bool = False  # Changed default to False for CBT
    ) -> str:
        """
        Generate SSML markup for natural, realistic speech.
        
        Args:
            text: Plain text to convert to SSML
            language: Language mode ('english', 'hindi', 'hinglish').
                     If None, auto-detects from text.
            rate: Speaking rate (e.g., "94%"). If None, uses default.
            pitch: Voice pitch (e.g., "-2.2st"). If None, uses default.
            add_breath: Whether to add breathing sounds/pauses
            add_intro: Whether to add natural intro filler
            
        Returns:
            SSML markup string
        """
        # Auto-detect language if not provided
        if language is None:
            language = SSMLGenerator.detect_language_from_text(text)
            logger.info(f"Auto-detected language: {language}")
        
        # Use default prosody if not specified
        rate = rate or SSMLGenerator.DEFAULT_RATE
        pitch = pitch or SSMLGenerator.DEFAULT_PITCH
        
        # Clean text (remove any existing SSML tags)
        text = re.sub(r'<[^>]+>', '', text)
        
        # Add natural pauses
        text = SSMLGenerator.add_natural_pauses(text)
        
        # Add emphasis to important words
        text = SSMLGenerator.add_emphasis(text)
        
        # Build SSML content
        content_parts = []
        
        # Add breathing sound or pause at start
        if add_breath:
            content_parts.append(f'<break time="{SSMLGenerator.PAUSES["medium"]}"/>')
        
        # Add natural intro filler (optional for CBT - can be distracting)
        if add_intro:
            intro = SSMLGenerator.LANGUAGE_INTROS.get(language, "")
            if intro:
                content_parts.append(f'{intro} <break time="{SSMLGenerator.PAUSES["medium"]}"/>')
        
        # Add main text
        content_parts.append(text)
        
        # Add final breath pause
        if add_breath:
            content_parts.append(f'<break time="{SSMLGenerator.PAUSES["breath"]}"/>')
        
        # Combine all parts
        content = '\n        '.join(content_parts)
        
        # Generate final SSML
        ssml = f"""<speak>
  <prosody rate="{rate}" pitch="{pitch}">
        {content}
  </prosody>
</speak>"""
        
        logger.debug(f"Generated SSML for {language}: {ssml[:100]}...")
        
        return ssml


# Convenience function for easy import
def generate_ssml(text: str, language: Optional[str] = None, **kwargs) -> str:
    """
    Generate SSML markup for natural, realistic speech.
    
    Args:
        text: Plain text to convert to SSML
        language: Language mode ('english', 'hindi', 'hinglish')
        **kwargs: Additional options (rate, pitch, add_breath, add_intro)
        
    Returns:
        SSML markup string
    """
    return SSMLGenerator.generate_ssml(text, language, **kwargs)
