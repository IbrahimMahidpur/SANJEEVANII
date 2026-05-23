"""
Test Hindi word detection after fixes.
Verify that English words are NOT counted as Hindi.
"""

from june.june_va.language_detector import LanguageDetector

print("=" * 70)
print("🧪 TESTING HINDI WORD DETECTION - After Fixes")
print("=" * 70)

test_cases = [
    {
        "text": "It is lovely to finally chat with you",
        "expected_lang": "en-IN",
        "expected_hindi_words": 0,
        "description": "Pure English - should have 0 Hindi words"
    },
    {
        "text": "can help prevent relapses and reduce the risk",
        "expected_lang": "en-IN",
        "expected_hindi_words": 0,
        "description": "English medical text - should have 0 Hindi words"
    },
    {
        "text": "the best cure for malaria",
        "expected_lang": "en-IN",
        "expected_hindi_words": 0,
        "description": "English with 'the' - should NOT count as Hindi"
    },
    {
        "text": "Kya tum joke suna sakte ho?",
        "expected_lang": "hi-IN",
        "expected_hindi_words": 5,  # kya, tum, suna, sakte, ho
        "description": "Hinglish question - should have multiple Hindi words"
    },
    {
        "text": "main tumse baat karna chahta hoon",
        "expected_lang": "hi-IN",
        "expected_hindi_words": 6,  # main, tumse, baat, karna, chahta, hoon
        "description": "Pure Hindi (transliterated) - should have many Hindi words"
    },
    {
        "text": "Hello, kaise ho aap?",
        "expected_lang": "hi-IN",
        "expected_hindi_words": 3,  # kaise, ho, aap
        "description": "Hinglish greeting - should detect Hindi words"
    }
]

passed = 0
failed = 0

for i, test in enumerate(test_cases, 1):
    text = test["text"]
    expected_lang = test["expected_lang"]
    expected_hindi = test["expected_hindi_words"]
    description = test["description"]
    
    # Run detection
    detected_lang, _ = LanguageDetector.detect_language(text)
    hindi_count = LanguageDetector.count_hindi_words(text)
    
    # Check results
    lang_correct = detected_lang == expected_lang
    count_correct = hindi_count == expected_hindi
    
    status = "✅ PASS" if (lang_correct and count_correct) else "❌ FAIL"
    if lang_correct and count_correct:
        passed += 1
    else:
        failed += 1
    
    print(f"\n{status} Test {i}: {description}")
    print(f"   Text: '{text}'")
    print(f"   Hindi words: {hindi_count} (expected: {expected_hindi}) {'✅' if count_correct else '❌'}")
    print(f"   Detected lang: {detected_lang} (expected: {expected_lang}) {'✅' if lang_correct else '❌'}")

print("\n" + "=" * 70)
print(f"📊 RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
print("=" * 70)

if failed == 0:
    print("✅ All tests passed! Hindi word detection is working correctly.")
else:
    print(f"⚠️  {failed} test(s) failed. Check the Hindi word dictionary.")
