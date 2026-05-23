import requests

# Simple test to check if TTS is generating audio
print("Testing TTS endpoint...")

# Create minimal audio file
test_audio = b'\x00' * 5000

files = {'file': ('test.webm', test_audio, 'audio/webm')}
data = {'session_id': 'simple_test', 'language': 'en-US'}

try:
    response = requests.post(
        "http://localhost:8002/voice-session",
        files=files,
        data=data,
        timeout=60
    )
    
    print(f"\nStatus: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")
    
    if response.status_code == 200:
        audio_size = len(response.content)
        print(f"Audio size: {audio_size} bytes")
        
        if audio_size > 0:
            with open("test_tts_output.mp3", "wb") as f:
                f.write(response.content)
            print(f"✓ Audio saved to test_tts_output.mp3")
            print(f"\nPlay this file to verify TTS is working!")
        else:
            print("✗ Audio is empty!")
    else:
        print(f"✗ Error: {response.text[:200]}")
        
except Exception as e:
    print(f"✗ Failed: {e}")
