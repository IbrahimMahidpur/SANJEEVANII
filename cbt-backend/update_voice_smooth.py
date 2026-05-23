import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update synthesize_tts to use speaking_rate=0.97, pitch=-2.0
# Previous: audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.MP3, speaking_rate=0.95, pitch=-3.0)
# Target: audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.MP3, speaking_rate=0.97, pitch=-2.0)

# Use regex to replace the audio_config line to be safe regardless of previous values
content = re.sub(
    r'audio_config\s*=\s*tts\.AudioConfig\(.*?\)', 
    'audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.MP3, speaking_rate=0.97, pitch=-2.0)', 
    content
)

# 2. Update SSML wrapper to be ULTRA CLEAN: <speak>{safe_reply}</speak>
# We previously made it <speak>{safe_reply}</speak> in the last step, but let's ensure it.
# The user asked for:
# <speak>
#   <prosody rate="97%" pitch="-2st">
#     {TEXT_HERE}
#   </prosody>
# </speak>
# BUT provided AudioConfig too. To avoid double application, I'll stick to AudioConfig 
# for the rate/pitch and plain SSML. UNLESS the user implies that the SSML structure ITSELF 
# triggers better flow. 
# Let's try combining: AudioConfig is global. SSML is markup.
# I'll stick to the minimalist wrapper + AudioConfig. It's the most robust way to get "Google decided" pauses.

ssml_replacement = '        ssml = f"""<speak>{safe_reply}</speak>"""'
# We will replace whatever the current ssml definition is. 
# It's likely spanning multiple lines or one line.
# let's look for the ssml = f"""<speak>... block again.

# Regex to find the ssml assignment block
content = re.sub(
    r'ssml\s*=\s*f"""<speak>.*?</speak>"""', 
    'ssml = f"""<speak>{safe_reply}</speak>"""', 
    content, 
    flags=re.DOTALL
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Applied Smoothest Hinglish Voice settings (0.97/-2.0)")
