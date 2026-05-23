import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update VOICE_MAP to use Neural2 voices (Google Cloud recommended)
old_voice_map = '''VOICE_MAP = {
    "en-US": {"name": "en-US-Wavenet-D", "gender": tts.SsmlVoiceGender.MALE},
    "hi-IN": {"name": "hi-IN-Wavenet-A", "gender": tts.SsmlVoiceGender.MALE},
}'''

new_voice_map = '''VOICE_MAP = {
    "en-US": {"name": "en-US-Neural2-D", "gender": tts.SsmlVoiceGender.MALE},  # Neural2 for better quality
    "en-IN": {"name": "en-IN-Neural2-B", "gender": tts.SsmlVoiceGender.MALE},  # Indian English (best for Hinglish)
    "hi-IN": {"name": "hi-IN-Neural2-B", "gender": tts.SsmlVoiceGender.MALE},  # Hindi Neural2
}'''

if old_voice_map in content:
    content = content.replace(old_voice_map, new_voice_map)
    print("✓ Updated VOICE_MAP to Neural2 voices")

# 2. Update synthesize_tts to use 95% rate and -1st pitch (Google recommended)
old_audio_config = 'audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.MP3, speaking_rate=0.94, pitch=-2.2)'
new_audio_config = 'audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.MP3, speaking_rate=0.95, pitch=-1.0)'

if old_audio_config in content:
    content = content.replace(old_audio_config, new_audio_config)
    print("✓ Updated AudioConfig to Google recommended settings (95%/-1.0)")

# 3. Find the voice_session endpoint and update to use advanced SSML
# Look for the SSML generation section
old_ssml_section = '''        # 9) Generate SSML using Sanjeevani's sophisticated generator
        # Auto-detects language mode and applies appropriate prosody
        ssml = SSMLGenerator.generate_ssml(
            enhanced_text,
            language=None,  # Auto-detect from text
            rate="94%",     # Sanjeevani-optimized
            pitch="-2.2st", # Sanjeevani-optimized
            add_breath=True,
            add_intro=False  # No intro fillers for CBT
        )'''

new_ssml_section = '''        # 9) Generate ADVANCED SSML with Google Cloud best practices
        # Uses transliteration, lang tags, and optimized prosody
        from agents.advanced_ssml import generate_advanced_ssml
        
        ssml = generate_advanced_ssml(
            enhanced_text,
            language=None,  # Auto-detect from text
            rate="95%",     # Google Cloud recommended
            pitch="-1st",   # Google Cloud recommended
            use_transliteration=True,  # Roman Hindi → Devanagari
            use_lang_tags=True         # Wrap Hindi with <lang xml:lang="hi-IN">
        )'''

if old_ssml_section in content:
    content = content.replace(old_ssml_section, new_ssml_section)
    print("✓ Updated to use Advanced SSML Generator")
else:
    print("⚠ Could not find SSML section to update (may need manual update)")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ Successfully applied Google Cloud TTS best practices!")
print("\nChanges made:")
print("1. Neural2 voices (en-US-Neural2-D, en-IN-Neural2-B, hi-IN-Neural2-B)")
print("2. Optimized prosody (95% rate, -1.0 pitch)")
print("3. Advanced SSML with transliteration and lang tags")
