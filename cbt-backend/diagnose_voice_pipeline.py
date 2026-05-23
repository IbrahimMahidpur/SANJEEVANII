"""
Complete Voice Pipeline Diagnostic Script
Tests each component of the voice therapy system
"""

import requests
import json
import os
import time

def test_backend_health():
    """Test if backend is responding"""
    try:
        response = requests.get("http://localhost:8002/", timeout=5)
        print(f"✓ Backend health check: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Backend health check failed: {e}")
        return False

def test_voice_endpoint():
    """Test voice-session endpoint with dummy audio"""
    try:
        # Create minimal test audio
        test_audio = b'\x00' * 1000  # 1KB of silence
        
        files = {'file': ('test.webm', test_audio, 'audio/webm')}
        data = {
            'session_id': 'diagnostic_test',
            'language': 'hi-IN'
        }
        
        print("\n[Testing voice-session endpoint...]")
        response = requests.post(
            "http://localhost:8002/voice-session",
            files=files,
            data=data,
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"Content-Length: {response.headers.get('content-length')} bytes")
        
        if response.status_code == 200:
            audio_size = len(response.content)
            print(f"✓ Audio response received: {audio_size} bytes")
            
            # Save for inspection
            with open("diagnostic_output.mp3", "wb") as f:
                f.write(response.content)
            print(f"✓ Audio saved to diagnostic_output.mp3")
            
            # Check if audio is too small
            if audio_size < 5000:
                print(f"⚠ WARNING: Audio file very small ({audio_size} bytes)")
                print("  This suggests LLM response is too brief")
            
            return True
        else:
            print(f"✗ Error response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"✗ Voice endpoint test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_google_credentials():
    """Check if Google Cloud credentials are set"""
    creds = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    if creds:
        print(f"✓ Google credentials set: {creds}")
        if os.path.exists(creds):
            print(f"✓ Credentials file exists")
            return True
        else:
            print(f"✗ Credentials file not found!")
            return False
    else:
        print(f"✗ GOOGLE_APPLICATION_CREDENTIALS not set")
        return False

def main():
    print("="*60)
    print("CBT VOICE PIPELINE DIAGNOSTIC")
    print("="*60)
    
    # Test 1: Backend Health
    print("\n[1] Testing Backend Health...")
    backend_ok = test_backend_health()
    
    # Test 2: Google Credentials
    print("\n[2] Checking Google Cloud Credentials...")
    creds_ok = check_google_credentials()
    
    # Test 3: Voice Endpoint
    print("\n[3] Testing Voice Endpoint...")
    voice_ok = test_voice_endpoint()
    
    # Summary
    print("\n" + "="*60)
    print("DIAGNOSTIC SUMMARY")
    print("="*60)
    print(f"Backend Health:    {'✓ PASS' if backend_ok else '✗ FAIL'}")
    print(f"Google Credentials: {'✓ PASS' if creds_ok else '✗ FAIL'}")
    print(f"Voice Endpoint:     {'✓ PASS' if voice_ok else '✗ FAIL'}")
    
    if backend_ok and creds_ok and voice_ok:
        print("\n✓ All tests passed! System is working.")
        print("  If you still can't hear audio:")
        print("  1. Check system volume")
        print("  2. Check browser tab is not muted")
        print("  3. Try with headphones")
        print("  4. Check browser console for errors")
    else:
        print("\n✗ Some tests failed. Check errors above.")

if __name__ == "__main__":
    main()
