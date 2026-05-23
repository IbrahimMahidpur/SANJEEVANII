import requests
import os
from google.cloud import texttospeech

# 1. Generate Test Audio (Simulating User Voice)
def generate_test_audio(text="I am feeling very anxious about my upcoming exam.", filename="test_input.wav"):
    print(f"Generating test audio: '{text}'...")
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16)
    
    response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
    
    with open(filename, "wb") as out:
        out.write(response.audio_content)
    print(f"Saved {filename}")
    return filename

# 2. Send to Backend
def test_backend(input_file="test_input.wav"):
    url = "http://localhost:8002/voice-session"
    print(f"Sending {input_file} to {url}...")
    
    with open(input_file, "rb") as f:
        files = {"file": (input_file, f, "audio/wav")}
        data = {"language": "en-US"}
        
        try:
            response = requests.post(url, files=files, data=data, timeout=60)
            
            if response.status_code == 200:
                print("Success! Backend returned 200 OK.")
                output_file = "test_output.mp3"
                with open(output_file, "wb") as out:
                    out.write(response.content)
                print(f"Saved response to {output_file}")
                print(f"Response size: {len(response.content)} bytes")
            else:
                print(f"Failed! Status: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    # Ensure credentials are set (same as app.py)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vaani-474822-36de07e0981f.json")
    
    try:
        generate_test_audio()
        test_backend()
    except Exception as e:
        print(f"Test failed: {e}")
