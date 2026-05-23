import requests
import json

# Test the voice endpoint
url = "http://localhost:8002/voice_session"

# Create a simple test audio file (empty for now, just to test the endpoint)
files = {
    'audio': ('test.webm', b'test', 'audio/webm')
}

data = {
    'session_id': 'test123',
    'language': 'hinglish'
}

try:
    print("Sending request to backend...")
    response = requests.post(url, files=files, data=data, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
