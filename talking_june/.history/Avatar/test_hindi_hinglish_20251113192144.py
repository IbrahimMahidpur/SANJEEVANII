"""
Test script to validate Hindi/Hinglish language detection and response matching.

This script tests the improved language detection and ensures responses match input language.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'june'))

from june_va.language_detector import LanguageDetector
from june_va.utils import detect_language_mode


def test_language_detection():
    """Test language detection with various inputs."""
    
    test_cases = [
        # (input_text, expected_lang, description)
        ("Hello, how are you?", "english", "Pure English"),
        ("मुझे आपकी मदद चाहिए", "hindi", "Pure Hindi (Devanagari)"),
        ("Mujhe help chahiye", "hindi", "Transliterated Hindi"),
        ("Kya aap mera kaam kar sakte ho?", "hinglish", "Hinglish (Hindi verbs + English)"),
        ("Main help kar sakta hoon", "hindi", "Hindi with English word"),
        ("Aap theek ho? How are you?", "hinglish", "Code-mixed Hinglish"),
        ("Can you batao how this works?", "hinglish", "English with Hindi verb"),
        ("Haan bilkul! That's perfect.", "hinglish", "Hinglish confirmation"),
        ("Thoda wait karo please", "hinglish", "Hinglish polite request"),
        ("What is the matlab of this?", "hinglish", "English with Hindi noun"),
        ("Mujhe nahi pata", "hindi", "Pure Hindi phrase"),
        ("Kya hai yeh?", "hindi", "Hindi question"),
        ("Tell me ek joke", "hinglish", "English request + Hindi word"),
        ("আমি তোমার সাহায্য চাই", "hindi", "Bengali script (treated as Hindi mode)"),
        ("Please help me", "english", "Polite English request"),
    ]
    
    print("=" * 80)
    print("LANGUAGE DETECTION TEST RESULTS")
    print("=" * 80)
    print()
    
    passed = 0
    failed = 0
    
    for text, expected, description in test_cases:
        detected = detect_language_mode(text)
        status = "✅ PASS" if detected == expected else "❌ FAIL"
        
        if detected == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} | {description}")
        print(f"  Input:    \"{text}\"")
        print(f"  Expected: {expected}")
        print(f"  Detected: {detected}")
        
        # Also show detailed detection
        lang_code, _ = LanguageDetector.detect_language(text)
        is_hinglish = LanguageDetector.is_hinglish(text)
        hindi_count = LanguageDetector.count_hindi_words(text)
        english_count = LanguageDetector.count_english_words(text)
        
        print(f"  Details:  lang_code={lang_code}, hinglish={is_hinglish}, "
              f"hindi_words={hindi_count}, english_words={english_count}")
        print()
    
    print("=" * 80)
    print(f"SUMMARY: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 80)
    print()
    
    return failed == 0


def test_hinglish_patterns():
    """Test Hinglish pattern detection."""
    
    print("=" * 80)
    print("HINGLISH PATTERN DETECTION TEST")
    print("=" * 80)
    print()
    
    hinglish_examples = [
        "Kya tum mujhe help kar sakte ho?",
        "Main abhi going to the store",
        "Yeh kaam bahut difficult hai",
        "Aaj ka weather kaisa hai?",
        "Please mujhe batao",
        "I don't know yaar",
        "Thoda wait karo",
        "Kya aap ready ho?",
    ]
    
    for text in hinglish_examples:
        is_hinglish = LanguageDetector.is_hinglish(text)
        status = "✅" if is_hinglish else "❌"
        print(f"{status} \"{text}\" → Hinglish: {is_hinglish}")
    
    print()


def test_llm_prompt_generation():
    """Test that correct prompts are generated for each language mode."""
    
    print("=" * 80)
    print("LLM PROMPT GENERATION TEST")
    print("=" * 80)
    print()
    
    test_inputs = [
        ("Hello, can you help me?", "english"),
        ("Kya aap meri madad kar sakte ho?", "hinglish"),
        ("मुझे सहायता चाहिए", "hindi"),
    ]
    
    for text, expected_mode in test_inputs:
        detected_mode = detect_language_mode(text)
        status = "✅ PASS" if detected_mode == expected_mode else "❌ FAIL"
        
        print(f"{status} Input: \"{text}\"")
        print(f"  Expected Mode: {expected_mode}")
        print(f"  Detected Mode: {detected_mode}")
        
        # Show what prompt would be used
        if detected_mode == 'hinglish':
            prompt_info = "Will use Hinglish prompt with 'MUST respond in Hinglish'"
        elif detected_mode == 'hindi':
            prompt_info = "Will use Hindi prompt with 'MUST respond in Hindi'"
        else:
            prompt_info = "Will use English prompt"
        
        print(f"  LLM Prompt: {prompt_info}")
        print()


def test_tts_language_selection():
    """Test TTS language selection based on response content."""
    
    print("=" * 80)
    print("TTS LANGUAGE SELECTION TEST")
    print("=" * 80)
    print()
    
    response_texts = [
        ("Sure, I can help you with that.", "en-IN", "Pure English"),
        ("Haan bilkul! Main aapki madad kar sakta hoon.", "en-IN", "Hinglish response"),
        ("हाँ, मैं आपकी मदद कर सकता हूं।", "hi-IN", "Hindi Devanagari"),
        ("Main aapko help karunga.", "hi-IN", "Transliterated Hindi"),
        ("Of course! Let me check that for you.", "en-IN", "English"),
    ]
    
    for text, expected_lang, description in response_texts:
        detected_lang, _ = LanguageDetector.detect_language(text)
        optimal_lang = LanguageDetector.get_optimal_tts_language(detected_lang, text)
        status = "✅ PASS" if optimal_lang == expected_lang else "⚠️  CHECK"
        
        print(f"{status} | {description}")
        print(f"  Response: \"{text[:50]}...\"")
        print(f"  Detected: {detected_lang} → Optimal TTS: {optimal_lang}")
        print(f"  Expected: {expected_lang}")
        print()


if __name__ == "__main__":
    print("\n🚀 Starting Hindi/Hinglish Language Detection Tests\n")
    
    # Run all tests
    test_language_detection()
    test_hinglish_patterns()
    test_llm_prompt_generation()
    test_tts_language_selection()
    
    print("=" * 80)
    print("✅ All tests completed!")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Run the full system with: run_all.bat")
    print("2. Test with Hindi: 'Mujhe help chahiye'")
    print("3. Test with Hinglish: 'Kya aap joke suna sakte ho?'")
    print("4. Test with English: 'Can you help me?'")
    print()
    print("Check logs for:")
    print("  - 'Detected language mode: ...'")
    print("  - 'STT detected: ..., Response detected: ...'")
    print("  - 'TTS will use: ...'")
    print()
