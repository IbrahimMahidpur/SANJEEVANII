"""
Hinglish Text Processor - Refines text for ultra-natural Hinglish speech.
Adapted from Sanjeevani module for CBT therapy context.

This module processes LLM output to ensure smooth, natural Hinglish with:
- Roman Hindi (not Devanagari)
- Natural fillers (achha, dekhiye, theek hai)
- Short, conversational sentences
- Warm, caring tone
"""

import re
from typing import List


class HinglishProcessor:
    """Process text to make it sound ultra-natural in Hinglish."""
    
    # Natural Hinglish fillers
    FILLERS = [
        "achha", "dekhiye", "haan", "okay", "theek hai", 
        "bilkul", "araam se", "thoda sa"
    ]
    
    # CBT-specific caring phrases
    CARING_STARTERS = [
        "Achha… ",
        "Dekhiye… ",
        "Haan bilkul… ",
        "Suniye… ",
    ]
    
    CARING_CLOSERS = [
        "… okay?",
        "… theek hai?",
        "… tension mat lijiye",
        "… sab theek ho jayega",
        "… aap akele nahi hain",
    ]
    
    @staticmethod
    def add_natural_pauses(text: str) -> str:
        """Add natural pauses and fillers for conversational flow."""
        # Replace periods with ellipsis for natural pauses
        text = re.sub(r'\.\s+', '… ', text)
        # Replace commas with ellipsis for flow
        text = re.sub(r',\s+', '… ', text)
        return text
    
    @staticmethod
    def break_long_sentences(text: str) -> str:
        """Break long sentences into shorter, natural chunks."""
        # Split on sentence boundaries
        sentences = re.split(r'[.!?।]+', text)
        
        processed = []
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # If sentence is too long (>60 chars), try to break it
            if len(sentence) > 60:
                # Break on conjunctions (Hindi/Hinglish)
                parts = re.split(r'\b(aur|lekin|par|toh|na|ki|kyunki)\b', sentence)
                processed.extend([p.strip() for p in parts if p.strip()])
            else:
                processed.append(sentence)
        
        return '… '.join(processed) + '.'
    
    @staticmethod
    def ensure_roman_hindi(text: str) -> str:
        """Ensure Hindi is in Roman script, not Devanagari."""
        # Check if text contains Devanagari characters
        devanagari_pattern = re.compile(r'[\u0900-\u097F]+')
        
        if devanagari_pattern.search(text):
            # Filter out Devanagari (already done in therapy_response.py)
            # This is a backup
            text = ''.join(char for char in text 
                          if not ('\u0900' <= char <= '\u097F'))
        
        return text
    
    @staticmethod
    def add_caring_tone(text: str) -> str:
        """Add warm, caring elements to the text."""
        # Add reassuring phrases at the start
        # Only for longer responses (>30 chars)
        if len(text) > 30:
            # Check if it already starts with a caring phrase
            if not any(text.startswith(s.strip()) for s in HinglishProcessor.CARING_STARTERS):
                # Add a caring starter
                text = "Achha… " + text
        
        return text
    
    @staticmethod
    def process(text: str) -> str:
        """
        Main processing function - refines text for ultra-natural Hinglish.
        
        Args:
            text: Raw text from LLM
            
        Returns:
            Processed text optimized for natural Hinglish TTS
        """
        if not text or not text.strip():
            return text
        
        # 1. Ensure Roman Hindi (not Devanagari)
        text = HinglishProcessor.ensure_roman_hindi(text)
        
        # 2. Break long sentences
        text = HinglishProcessor.break_long_sentences(text)
        
        # 3. Add natural pauses (ellipsis)
        text = HinglishProcessor.add_natural_pauses(text)
        
        # 4. Add caring tone elements
        text = HinglishProcessor.add_caring_tone(text)
        
        # 5. Clean up excessive punctuation
        text = re.sub(r'\.{2,}', '…', text)  # Multiple dots → ellipsis
        text = re.sub(r'…{2,}', '… ', text)  # Multiple ellipsis → single
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces → single space
        text = text.strip()
        
        return text
    
    @staticmethod
    def process_for_tts(text: str) -> str:
        """
        Lightweight processing specifically for TTS.
        Focuses on pronunciation and natural flow.
        
        Args:
            text: Text to process
            
        Returns:
            TTS-optimized text
        """
        if not text or not text.strip():
            return text
        
        # Remove markdown formatting
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.+?)\*', r'\1', text)  # Italic
        text = re.sub(r'__(.+?)__', r'\1', text)  # Underline
        text = re.sub(r'_(.+?)_', r'\1', text)  # Underline
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)  # Headers
        
        # Add natural pauses for better TTS rhythm
        text = HinglishProcessor.add_natural_pauses(text)
        
        # Clean up
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text


# Convenience function for easy import
def process_hinglish(text: str) -> str:
    """Process text for ultra-natural Hinglish."""
    return HinglishProcessor.process(text)


def process_for_tts(text: str) -> str:
    """Process text for TTS with natural flow."""
    return HinglishProcessor.process_for_tts(text)
