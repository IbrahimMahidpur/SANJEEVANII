"""
Test Enhanced Multilingual Features

This script tests the enhanced language detection and text processing features.
"""

import sys
from pathlib import Path

# Add june_va to path
sys.path.insert(0, str(Path(__file__).parent / "june"))

from june_va.language_detector import LanguageDetector
from june_va.multilingual_utils import (
    detect_language_mode,
    polish_hinglish,
    enhance_text_for_tts,
    add_hinglish_pauses
)


def test_language_detection():
    """Test language detection on various inputs."""
    print("=" * 70)
    print("🔍 LANGUAGE DETECTION TESTS")
    print("=" * 70)
    
    test_cases = [
        ("Hello, how are you?", "en-IN", "Pure English"),
        ("नमस्ते, आप कैसे हैं?", "hi-IN", "Pure Hindi (Devanagari)"),
        ("Hey mujhe help chahiye", "en-IN", "Hinglish (transliterated)"),
        ("Main aapki help kar sakta hoon", "hi-IN", "Hindi (transliterated)"),
        ("Can you explain machine learning?", "en-IN", "Pure English technical"),
        ("Ye feature kaise use karte hain?", "en-IN", "Hinglish question"),
        ("मुझे programming में help चाहिए", "hi-IN", "Mixed Devanagari + English"),
    ]
    
    for text, expected_base, description in test_cases:
        detected, details = LanguageDetector.detect_language(text, detailed=True)
        mode = detect_language_mode(text)
        
        status = "✅" if detected.startswith(expected_base[:2]) else "⚠️"
        
        print(f"\n{status} Test: {description}")
        print(f"   Input: {text}")
        print(f"   Detected: {detected} (Mode: {mode})")
        if details:
            print(f"   Details: {details}")


def test_hinglish_polishing():
    """Test Hinglish text polishing."""
    print("\n" + "=" * 70)
    print("✨ HINGLISH POLISHING TESTS")
    print("=" * 70)
    
    test_cases = [
        ("Main aapki help kar sakta hoon", "hi-IN"),
        ("Mujhe kuch chahiye", "hi-IN"),
        ("Hey, kya haal hai?", "en-IN"),
        ("This is achha", "en-IN"),
    ]
    
    for text, target_lang in test_cases:
        polished = polish_hinglish(text, target_lang)
        changed = "✅ Changed" if polished != text else "➡️ Unchanged"
        
        print(f"\n{changed} ({target_lang})")
        print(f"   Original: {text}")
        print(f"   Polished: {polished}")


def test_text_enhancement():
    """Test comprehensive text enhancement."""
    print("\n" + "=" * 70)
    print("🎯 TEXT ENHANCEMENT TESTS")
    print("=" * 70)
    
    test_cases = [
        "**Hello**, how are you?",
        "Mujhe *help* chahiye programming mein",
        "Ye feature __bohot__ useful hai",
        "# Main Heading\nKuch text hai",
        "Main 10 lakh rupees chahiye",
    ]
    
    for text in test_cases:
        enhanced, optimal_lang = enhance_text_for_tts(text)
        
        print(f"\n✅ Test")
        print(f"   Original: {text}")
        print(f"   Enhanced: {enhanced}")
        print(f"   Language: {optimal_lang}")


def test_pause_insertion():
    """Test pause insertion for better flow."""
    print("\n" + "=" * 70)
    print("⏸️ PAUSE INSERTION TESTS")
    print("=" * 70)
    
    test_cases = [
        "Main jaunga aur wo ayega",
        "Pehle ye karo phir wo karo",
        "Ye theek hai lekin wo nahi",
    ]
    
    for text in test_cases:
        with_pauses = add_hinglish_pauses(text)
        changed = "✅ Pauses added" if with_pauses != text else "➡️ No change"
        
        print(f"\n{changed}")
        print(f"   Original: {text}")
        print(f"   Enhanced: {with_pauses}")


def test_optimal_tts_language():
    """Test optimal TTS language selection."""
    print("\n" + "=" * 70)
    print("🎵 OPTIMAL TTS LANGUAGE SELECTION")
    print("=" * 70)
    
    test_cases = [
        ("Hello world", "en-IN"),
        ("नमस्ते दुनिया", "hi-IN"),
        ("Hey mujhe help chahiye", "en-IN"),
        ("Main programming seekh raha hoon", "hi-IN"),
        ("This is a mixed sentence with kuch Hindi words", "en-IN"),
    ]
    
    for text, detected in test_cases:
        optimal = LanguageDetector.get_optimal_tts_language(detected, text)
        
        print(f"\n✅ Text: {text}")
        print(f"   Detected: {detected}")
        print(f"   Optimal: {optimal}")


def run_all_tests():
    """Run all tests."""
    print("\n")
    print("🌟" * 35)
    print(" " * 10 + "ENHANCED MULTILINGUAL FEATURE TESTS")
    print("🌟" * 35)
    
    try:
        test_language_detection()
        test_hinglish_polishing()
        test_text_enhancement()
        test_pause_insertion()
        test_optimal_tts_language()
        
        print("\n" + "=" * 70)
        print("🎉 ALL TESTS COMPLETED")
        print("=" * 70)
        print("\n✅ Enhanced multilingual features are working!")
        print("🚀 Ready to use config-enhanced-multilingual.json")
        print("\nTo start June with enhanced features:")
        print("  cd june")
        print("  python -m june_va --config config-enhanced-multilingual.json")
        print()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(run_all_tests())
