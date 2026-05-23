import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update VOICE_MAP to use en-IN-Neural2-B
# This voice is recommended for Hinglish.
voice_map_replacement = '''VOICE_MAP = {
    "en-US": {"name": "en-IN-Neural2-B", "gender": tts.SsmlVoiceGender.MALE},
    "hi-IN": {"name": "en-IN-Neural2-B", "gender": tts.SsmlVoiceGender.MALE},  # Use Indian English voice for better Hinglish
}
DEFAULT_LANG = "en-US"'''

# Find existing VOICE_MAP block (approximate content)
# We'll use regex to find the variable definition
content = re.sub(r'VOICE_MAP\s*=\s*{[^}]*}\s*DEFAULT_LANG\s*=\s*"en-US"', voice_map_replacement, content, flags=re.DOTALL)


# 2. Update synthesize_tts to include pitch and rate in AudioConfig
# Existing: audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.MP3)
# New: audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.MP3, speaking_rate=0.95, pitch=-3.0)

audio_config_old = 'audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.MP3)'
audio_config_new = 'audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.MP3, speaking_rate=0.95, pitch=-3.0)'

if audio_config_old in content:
    content = content.replace(audio_config_old, audio_config_new)


# 3. Update SSML generation in voice_session to remove manual prosody (conflicts with AudioConfig)
# Existing: <prosody rate="90%" pitch="-2%" volume="soft">
# New: (Just the breaks, or maybe keep volume="soft" if needed? User didn't specify volume, but said "calm".
# I'll simply remove the prosody wrapper and keep the breaks.)

# We need to be careful with string replacement.
# Pattern:
# ssml = f"""<speak>
#             <prosody rate="90%" pitch="-2%" volume="soft">
#                 <break time="400ms"/>
#                 {safe_reply}
#                 <break time="600ms"/>
#             </prosody>
#         </speak>"""

# New Pattern:
# ssml = f"""<speak>
#             <break time="400ms"/>
#             {safe_reply}
#             <break time="600ms"/>
#         </speak>"""

# Let's verify the exact content from previous file read.
# Line 374: ssml = f"""<speak>
# Line 375:             <prosody rate="90%" pitch="-2%" volume="soft">
# Line 376:                 <break time="400ms"/>
# Line 377:                 {safe_reply}
# Line 378:                 <break time="600ms"/>
# Line 379:             </prosody>
# Line 380:         </speak>"""

ssml_block_old = '''        ssml = f"""<speak>
            <prosody rate="90%" pitch="-2%" volume="soft">
                <break time="400ms"/>
                {safe_reply}
                <break time="600ms"/>
            </prosody>
        </speak>"""'''

ssml_block_new = '''        ssml = f"""<speak>
            <break time="400ms"/>
            {safe_reply}
            <break time="600ms"/>
        </speak>"""'''

# Since whitespace might vary, let's target the lines explicitly or use regex if needed, 
# but direct replacement should work if I copied correctly from view_file output.
# I'll try simple replace first.
if ssml_block_old in content:
    content = content.replace(ssml_block_old, ssml_block_new)
else:
    # If indentation is tricky, try replacing specific lines
    content = content.replace('<prosody rate="90%" pitch="-2%" volume="soft">', '')
    content = content.replace('</prosody>', '')

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updates applied to app.py")
