"""
This module provides utility classes and functions.
"""

import logging
import os
import re
import sys
import threading
from typing import Any

from colorama import Fore, Style

logger = logging.getLogger(__name__)
_handler = logging.StreamHandler()
_formatter = logging.Formatter("%(message)s")
_handler.setFormatter(_formatter)
logger.addHandler(_handler)
logger.setLevel(logging.INFO)


class ThreadSafeState:
    """
    A thread-safe class for managing a shared state value.

    This class provides methods for setting and getting the value in a thread-safe manner
    using a lock.

    Args:
        value: The initial value of the shared state.

    Attributes:
        _value: The shared state value.
        _lock: A lock object used for thread-safe access to the shared state.
    """

    def __init__(self, value: Any) -> None:
        self._value = value
        self._lock = threading.Lock()

    def set_value(self, value: Any) -> None:
        """
        Set the shared state value in a thread-safe manner.

        Args:
            value: The new value to set for the shared state.
        """
        with self._lock:
            self._value = value

    def get_value(self) -> Any:
        """
        Get the shared state value in a thread-safe manner.

        Returns:
            The current value of the shared state.
        """
        with self._lock:
            return self._value


class suppress_stdout_stderr:
    """
    A context manager for temporarily suppressing stdout and stderr.

    This context manager redirects stdout and stderr to null files
    within the context, and restores them to their original values
    when the context is exited.
    """

    def __enter__(self) -> "suppress_stdout_stderr":
        """
        Suppresses stdout and stderr by redirecting them to null files.

        Returns:
            The instance of the context manager.
        """
        # Open null files for writing
        self.out_null_file = open(os.devnull, "w")
        self.err_null_file = open(os.devnull, "w")

        # Save original file descriptors
        self.old_stdout_file_no_undup = sys.stdout.fileno()
        self.old_stderr_file_no_undup = sys.stderr.fileno()

        # Duplicate file descriptors
        self.old_stdout_file_no = os.dup(sys.stdout.fileno())
        self.old_stderr_file_no = os.dup(sys.stderr.fileno())

        # Redirect stdout and stderr to null files
        os.dup2(self.out_null_file.fileno(), self.old_stdout_file_no_undup)
        os.dup2(self.err_null_file.fileno(), self.old_stderr_file_no_undup)

        # Save original stdout and stderr
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr

        # Set stdout and stderr to null files
        sys.stdout = self.out_null_file
        sys.stderr = self.err_null_file

        return self

    def __exit__(self, *_) -> None:
        """
        Restores stdout and stderr to their original values.
        """
        # Restore stdout and stderr
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr

        # Restore original file descriptors
        os.dup2(self.old_stdout_file_no, self.old_stdout_file_no_undup)
        os.dup2(self.old_stderr_file_no, self.old_stderr_file_no_undup)

        # Close duplicate file descriptors
        os.close(self.old_stdout_file_no)
        os.close(self.old_stderr_file_no)

        # Close null files
        self.out_null_file.close()
        self.err_null_file.close()


def deep_merge_dicts(old: dict, new: dict) -> dict:
    """
    Merge two dictionaries recursively.

    Args:
        old: The original dictionary.
        new: The new dictionary to merge into the original.

    Returns:
        The merged dictionary.
    """
    merged = old.copy()  # Start with a shallow copy of the old dictionary

    for key, value in new.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = deep_merge_dicts(merged[key], value)
        else:
            merged[key] = value

    return merged


def print_system_message(message: str, color: str = Fore.BLUE, log_level: int = logging.DEBUG) -> None:
    """
    Print a message with a colored system prompt.

    Args:
        message: The message to be printed.
        color: The color code for the message text (e.g., Fore.BLUE).
            Defaults to Fore.BLUE.
        log_level: The logging level for the message (e.g., logging.DEBUG).
            Defaults to logging.DEBUG.
    """
    logger.log(log_level, f"{Style.BRIGHT}{Fore.YELLOW}[system]> {Style.NORMAL}{color}{message}{Style.RESET_ALL}")


def detect_language_mode(text: str) -> str:
    """
    Detect whether text is Hinglish, English, or Hindi.
    Uses enhanced LanguageDetector for accurate detection.
    
    ⚡ OPTIMIZED: Prioritizes Hinglish for natural Indian conversations
    
    Args:
        text: Input text to analyze
        
    Returns:
        'hinglish' | 'english' | 'hindi'
        
    Examples:
        "Hello, how are you?" → 'english'
        "Kya tum joke suna sakte ho?" → 'hinglish'
        "Mujhe malaria hua hai" → 'hinglish' (default for transliterated Hindi)
        "नमस्ते" → 'hindi' (Devanagari)
    """
    from june_va.language_detector import LanguageDetector
    
    # Check for Devanagari script (pure Hindi)
    if LanguageDetector.has_devanagari(text):
        return 'hindi'
    
    # Use comprehensive language detector
    detected_lang, _ = LanguageDetector.detect_language(text)
    
    # Count Hindi and English words
    hindi_words = LanguageDetector.count_hindi_words(text)
    english_words = LanguageDetector.count_english_words(text)
    
    # ⚡ IMPROVED LOGIC: Default to Hinglish for Indian users
    if detected_lang == "hi-IN" or hindi_words > 0:
        # Any Hindi presence = Hinglish (most natural for Indians)
        return 'hinglish'
    elif detected_lang == "en-IN":
        # Check if it's Hinglish (code-mixed) or pure English
        if hindi_words > 0 or LanguageDetector.is_hinglish(text):
            return 'hinglish'
        # Only pure English if NO Hindi words detected
        elif english_words > 3 and hindi_words == 0:
            return 'english'
        else:
            # Default to Hinglish for short/ambiguous inputs
            return 'hinglish'
    elif detected_lang == "bn-IN":
        # Bengali - treat as Hinglish
        return 'hinglish'
    else:
        # Default: Hinglish (safest for Indian audience)
        return 'hinglish'


def polish_hinglish(text: str) -> str:
    """
    Polish Hinglish text for more natural flow and pronunciation.
    Fixes common grammatical patterns and repetitions.
    
    Args:
        text: Hinglish text to polish
        
    Returns:
        Polished text
    """
    # Remove repetitive words
    text = re.sub(r'\b(\w+)\s+\1\b', r'\1', text)  # "hai hai" → "hai"
    
    # Common spelling normalizations for better TTS
    replacements = {
        r'\bmai\b': 'main',           # "mai" → "main"
        r'\bnhi\b': 'nahi',           # "nhi" → "nahi"
        r'\bkro\b': 'karo',           # "kro" → "karo"
        r'\bkr\b': 'kar',             # "kr" → "kar"
        r'\bho\b(?=\s)': 'hai',       # Standalone "ho" → "hai" (context-dependent)
        r'\btheek\b': 'thik',         # Normalize spelling
    }
    
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Clean up extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text
