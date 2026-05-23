import requests

# Test TTS endpoint directly
url = "http://localhost:8002/voice-session"

# Create a test audio file (minimal webm)
test_audio = b'test audio data'

files = {
    'file': ('test.webm', test_audio, 'audio/webm')
}

data = {
    'session_id': 'test123',
    'language': 'hi-IN'
}

print("Testing voice-session endpoint...")
try:
    response = requests.post(url, files=files, data=data, timeout=60)
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")
    print(f"Content-Length: {response.headers.get('content-length')}")
    
    if response.status_code == 200:
        # Save the audio
        with open("test_output.mp3", "wb") as f:
            f.write(response.content)
        print(f"✓ Audio saved to test_output.mp3 ({len(response.content)} bytes)")
    else:
        print(f"✗ Error: {response.text}")
        
except Exception as e:
    print(f"✗ Exception: {e}")
