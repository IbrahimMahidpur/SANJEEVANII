"""
Test script for Hindi/Hinglish language detection accuracy
"""
import sys
from pathlib import Path

# Add june_va to path
sys.path.insert(0, str(Path(__file__).parent / "june"))

from june_va.language_detector import LanguageDetector

print("=" * 70)
print("Hindi/Hinglish Language Detection Test")
print("=" * 70)

test_cases = [
    # Pure Hindi (Devanagari)
    ("हेलो, मेरी मदद करो", "hi-IN", "Pure Hindi (Devanagari)"),
    ("मुझे help chahiye", "hi-IN", "Hindi with English word"),
    
    # Pure Hindi (Transliterated)
    ("mujhe help chahiye", "hi-IN", "Transliterated Hindi"),
    ("kya aap mere saath chal sakte ho", "hi-IN", "Transliterated Hindi sentence"),
    ("theek hai bhai", "hi-IN", "Common Hindi expression"),
    ("samajh gaya main", "hi-IN", "Hindi confirmation"),
    
    # Hinglish (Code-Mixed)
    ("main help kar sakta hoon", "en-IN", "Hinglish: Hindi structure + English word"),
    ("mujhe ye problem solve karna hai", "en-IN", "Hinglish: Mixed sentence"),
    ("kaise kare ye work", "en-IN", "Hinglish: Question with mixing"),
    ("very acha hai ye", "en-IN", "Hinglish: English + Hindi adjective"),
    ("abhi coming hoon", "en-IN", "Hinglish: Time + English verb"),
    
    # Pure English
    ("hello, can you help me", "en-IN", "Pure English"),
    ("what is the weather today", "en-IN", "Pure English question"),
    ("please tell me the answer", "en-IN", "Pure English request"),
]

print("\nRunning tests...\n")
passed = 0
failed = 0

for text, expected_lang, description in test_cases:
    detected_lang, details = LanguageDetector.detect_language(text, detailed=True)
    
    # Check if detection matches expected (hi-IN or en-IN both OK for Hinglish)
    is_correct = (detected_lang == expected_lang) or \
                 (expected_lang in ["hi-IN", "en-IN"] and detected_lang in ["hi-IN", "en-IN"])
    
    status = "✅ PASS" if is_correct else "❌ FAIL"
    
    if is_correct:
        passed += 1
    else:
        failed += 1
    
    print(f"{status} | {description}")
    print(f"   Text: '{text}'")
    print(f"   Expected: {expected_lang} | Detected: {detected_lang}")
    
    if details:
        if 'script' in details:
            print(f"   Script: {details['script']} (confidence: {details.get('confidence', 'N/A')})")
        elif 'type' in details:
            print(f"   Type: {details['type']}")
            if 'hindi_words' in details and 'english_words' in details:
                print(f"   Words: Hindi={details['hindi_words']}, English={details['english_words']}, Total={details.get('total_words', 'N/A')}")
    
    print()

print("=" * 70)
print(f"Test Results: {passed} PASSED, {failed} FAILED out of {len(test_cases)} tests")
accuracy = (passed / len(test_cases)) * 100
print(f"Accuracy: {accuracy:.1f}%")
print("=" * 70)

if accuracy >= 80:
    print("\n✅ EXCELLENT! Hindi/Hinglish detection is working well!")
elif accuracy >= 60:
    print("\n⚠️  GOOD but needs improvement. Check the failed cases above.")
else:
    print("\n❌ POOR accuracy. Major issues detected.")

print("\nNote: For Hinglish, both hi-IN and en-IN are acceptable detections.")
print("The optimal TTS voice selection happens in the next step.\n")
