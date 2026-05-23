import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add imports at the top (after existing imports)
import_block = """from google.cloud import speech_v1p1beta1 as speech
from google.cloud import texttospeech_v1 as tts

# Import Sanjeevani-style multilingual utilities
from agents.multilingual_utils import enhance_text_for_tts as sanjeevani_enhance
from agents.ssml_generator import SSMLGenerator
"""

# Find the import section and replace
old_imports = """from google.cloud import speech_v1p1beta1 as speech
from google.cloud import texttospeech_v1 as tts"""

if old_imports in content:
    content = content.replace(old_imports, import_block)
    print("✓ Added Sanjeevani imports")

# 2. Update synthesize_tts to use Sanjeevani settings (94%/-2.2st)
old_audio_config = 'audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.MP3, speaking_rate=0.97, pitch=-2.0)'
new_audio_config = 'audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.MP3, speaking_rate=0.94, pitch=-2.2)'

if old_audio_config in content:
    content = content.replace(old_audio_config, new_audio_config)
    print("✓ Updated AudioConfig to Sanjeevani settings (94%/-2.2)")

# 3. Remove the old enhance_for_tts function (we'll use Sanjeevani's)
# Find and remove the function
enhance_pattern = r'def enhance_for_tts\(text: str\) -\u003e str:.*?(?=\n(?:def |@app\.|# API Routes))'
content = re.sub(enhance_pattern, '', content, flags=re.DOTALL)
print("✓ Removed old enhance_for_tts function")

# 4. Update voice_session to use Sanjeevani's enhance and SSML
# Find the section where we clean and enhance text
old_section = """        # 8) Clean text for speech
        clean_response = enhance_for_tts(clean_text_for_speech(therapy_response))

        # 9) Create enhanced SSML for warm, caring voice
        safe_reply = clean_response.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        ssml = f\"\"\"<speak>
            {safe_reply}
        </speak>\"\"\""""

new_section = """        # 8) Enhance text using Sanjeevani's multilingual logic
        # This handles markdown removal, pause insertion, pronunciation mapping
        enhanced_text, optimal_lang = sanjeevani_enhance(therapy_response, language)
        
        # 9) Generate SSML using Sanjeevani's sophisticated generator
        # Auto-detects language mode and applies appropriate prosody
        ssml = SSMLGenerator.generate_ssml(
            enhanced_text,
            language=None,  # Auto-detect from text
            rate="94%",     # Sanjeevani-optimized
            pitch="-2.2st", # Sanjeevani-optimized
            add_breath=True,
            add_intro=False  # No intro fillers for CBT (can be distracting)
        )"""

if old_section in content:
    content = content.replace(old_section, new_section)
    print("✓ Updated voice_session to use Sanjeevani logic")
else:
    # Try a more flexible replacement
    # Find the clean_response line
    if 'clean_response = enhance_for_tts(clean_text_for_speech(therapy_response))' in content:
        content = content.replace(
            'clean_response = enhance_for_tts(clean_text_for_speech(therapy_response))',
            'enhanced_text, optimal_lang = sanjeevani_enhance(therapy_response, language)'
        )
        print("✓ Updated text enhancement call")
    
    # Find and replace SSML generation
    ssml_pattern = r'safe_reply = clean_response.*?ssml = f"""<speak>.*?</speak>"""'
    ssml_replacement = '''ssml = SSMLGenerator.generate_ssml(
            enhanced_text,
            language=None,  # Auto-detect from text
            rate="94%",     # Sanjeevani-optimized
            pitch="-2.2st", # Sanjeevani-optimized
            add_breath=True,
            add_intro=False  # No intro fillers for CBT
        )'''
    
    content = re.sub(ssml_pattern, ssml_replacement, content, flags=re.DOTALL)
    print("✓ Updated SSML generation")

# 5. Update the TTS call to use optimal_lang if available
# Find: audio_file = synthesize_tts(ssml, lang_code=language or DEFAULT_LANG, ssml=True)
# Replace with: audio_file = synthesize_tts(ssml, lang_code=optimal_lang or language or DEFAULT_LANG, ssml=True)
old_tts_call = 'audio_file = synthesize_tts(ssml, lang_code=language or DEFAULT_LANG, ssml=True)'
new_tts_call = 'audio_file = synthesize_tts(ssml, lang_code=optimal_lang if "optimal_lang" in locals() else (language or DEFAULT_LANG), ssml=True)'

if old_tts_call in content:
    content = content.replace(old_tts_call, new_tts_call)
    print("✓ Updated TTS call to use optimal language")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ Successfully integrated Sanjeevani voice system into app.py")
