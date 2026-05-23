from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid, os, aiofiles, requests, tempfile, json
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import texttospeech_v1 as tts
import asyncio
import subprocess
import traceback

# Set Google Cloud Credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vaani-474822-36de07e0981f.json")

app = FastAPI(title="CBT Voice Therapist API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- minimal voice mapping (expand by listing voices via API) ---
VOICE_MAP = {
    "en-US": {"name": "en-US-Wavenet-D", "gender": tts.SsmlVoiceGender.MALE},
    "hi-IN": {"name": "hi-IN-Wavenet-A", "gender": tts.SsmlVoiceGender.MALE},
    # add more languages...
}
DEFAULT_LANG = "en-US"

# --- Utilities ---
async def save_upload_tmp(upload: UploadFile) -> str:
    tmp = f"temp_{uuid.uuid4().hex}_{upload.filename}"
    async with aiofiles.open(tmp, 'wb') as out:
        content = await upload.read()
        await out.write(content)
    return tmp

def transcribe_gcloud(audio_path: str, language_hint: str=None, content_type: str=None):
    try:
        client = speech.SpeechClient()
        with open(audio_path, "rb") as f:
            content = f.read()
        
        print(f"[STT] Audio file size: {len(content)} bytes, Type: {content_type}")
        audio = {"content": content}

        # Enhanced encoding detection - let Google auto-detect sample rate for better accuracy
        encoding = speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED
        sample_rate = None  # Auto-detect by default
        
        if content_type:
            if "webm" in content_type:
                encoding = speech.RecognitionConfig.AudioEncoding.WEBM_OPUS
                # Don't set sample_rate - let Google detect it automatically
            elif "mpeg" in content_type or "mp3" in content_type:
                encoding = speech.RecognitionConfig.AudioEncoding.MP3
            elif "wav" in content_type:
                encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16
                try:
                    import wave
                    with wave.open(audio_path, "rb") as w:
                        sample_rate = w.getframerate()
                    print(f"[STT] WAV detected: {sample_rate}Hz")
                except Exception as e:
                    print(f"[STT] Error reading WAV header: {e}")

        # Enhanced recognition config for maximum accuracy
        config = {
            "language_code": language_hint or DEFAULT_LANG,
            "enable_automatic_punctuation": True,
            "model": "latest_long",  # Best model for longer audio
            "use_enhanced": True,  # Use enhanced models (better accuracy)
            "enable_word_confidence": True,  # Get per-word confidence
            "profanity_filter": False,  # Don't filter - therapy needs authentic speech
            "max_alternatives": 3,  # Get alternative transcriptions
        }
        
        # Add encoding only if detected
        if encoding != speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED:
            config["encoding"] = encoding
        
        # Only add sample rate if we know it (mainly for WAV)
        if sample_rate:
            config["sample_rate_hertz"] = sample_rate
        
        # Add alternative language codes for better multilingual support
        if language_hint and language_hint.startswith("en"):
            config["alternative_language_codes"] = ["hi-IN", "en-IN"]  # Support Hindi and Indian English
        elif language_hint and language_hint.startswith("hi"):
            config["alternative_language_codes"] = ["en-IN", "en-US"]  # Support English variants
        
        print(f"[STT] Config: model={config['model']}, enhanced={config.get('use_enhanced')}, lang={config['language_code']}")
        
        request = {"config": config, "audio": audio}
        resp = client.recognize(request=request)
        
        if not resp.results:
            msg = "[STT] No results - audio might be too quiet, unclear, or too short"
            print(msg)
            with open("cbt_debug.log", "a", encoding="utf-8") as f:
                f.write(msg + "\n")
            return "", None
        
        # Get best result
        best = resp.results[0].alternatives[0]
        transcript = best.transcript
        confidence = best.confidence if hasattr(best, 'confidence') else 1.0
        
        print(f"[STT] ✓ Transcript: '{transcript}' (confidence: {confidence:.2%})")
        
        # Log alternative transcriptions for debugging
        if len(resp.results[0].alternatives) > 1:
            print("[STT] Alternative transcriptions:")
            for i, alt in enumerate(resp.results[0].alternatives[1:], 1):
                alt_conf = alt.confidence if hasattr(alt, 'confidence') else 0.0
                print(f"[STT]   {i}. '{alt.transcript}' ({alt_conf:.2%})")
        
        # Warn if confidence is low
        if confidence < 0.7:
            print(f"[STT] ⚠️ Low confidence ({confidence:.2%}) - audio quality may be poor")
            with open("cbt_debug.log", "a", encoding="utf-8") as f:
                f.write(f"Low confidence: {confidence:.2%} for '{transcript}'\n")
        
        return transcript, confidence
        
    except Exception as e:
        error_msg = f"[STT] Error: {e}\n{traceback.format_exc()}"
        print(error_msg)
        with open("cbt_debug.log", "a", encoding="utf-8") as f:
            f.write(error_msg + "\n")
        return None, None

def call_local_llm(prompt_text: str, system_prompt: str):
    # Call Ollama API
    try:
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": "gpt-oss:120b-cloud", # User specified model
            "prompt": system_prompt + "\n\nUser: " + prompt_text + "\nTherapist:",
            "stream": False,
            "options": {
                "num_predict": 400,
                "stop": ["User:", "\n\n"]
            }
        }
        
        r = requests.post(url, json=payload, timeout=120) # Increased timeout for large model
        r.raise_for_status()
        return r.json().get("response","").strip()
    except Exception as e:
        print(f"LLM Error: {e}")
        return "I am having trouble connecting to my thoughts right now. Please try again."

def synthesize_tts(text: str, lang_code: str="en-US", voice_name: str=None, ssml=False):
    try:
        client = tts.TextToSpeechClient()
        if not voice_name:
            voice_info = VOICE_MAP.get(lang_code, VOICE_MAP.get(DEFAULT_LANG))
        else:
            voice_info = {"name": voice_name, "gender": tts.SsmlVoiceGender.MALE}
        
        if isinstance(voice_info, dict) and "name" in voice_info:
            voice_params = tts.VoiceSelectionParams(
                language_code=lang_code,
                name=voice_info["name"],
                ssml_gender=voice_info.get("gender", tts.SsmlVoiceGender.MALE)
            )
        else:
            voice_params = tts.VoiceSelectionParams(language_code=lang_code, ssml_gender=tts.SsmlVoiceGender.MALE)

        input_type = tts.SynthesisInput(ssml=text) if ssml else tts.SynthesisInput(text=text)
        audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.MP3)
        response = client.synthesize_speech(input=input_type, voice=voice_params, audio_config=audio_config)
        
        tmpfile = f"response_{uuid.uuid4().hex}.mp3"
        with open(tmpfile, "wb") as out:
            out.write(response.audio_content)
        return tmpfile
    except Exception as e:
        print(f"TTS Error: {e}")
        with open("cbt_debug.log", "a", encoding="utf-8") as f:
            f.write(f"TTS Error: {e}\n")
        return None

# --- Safety: simple crisis keyword list (expand & replace with ML classifier) ---
CRISIS_KEYWORDS = [
    "kill myself", "kill me", "i want to die", "suicide", "end my life",
    "hurt myself", "i'm going to jump", "i'm going to overdose", "i will kill myself"
]
def detect_crisis(text: str):
    t = text.lower()
    for k in CRISIS_KEYWORDS:
        if k in t:
            return True
    return False

SYSTEM_PROMPT = """# Role
You are an expert Cognitive Behavioural Therapist (CBT) with deep expertise in evidence-based therapeutic techniques, psychological assessment, and cross-cultural mental health support. You embody empathy, non-judgment, and professional boundaries while maintaining a warm, supportive demeanor. You are skilled at identifying thought patterns, challenging cognitive distortions, and guiding clients toward practical behavioral change. You communicate with cultural sensitivity and adapt your approach to diverse backgrounds and belief systems.

# Task
Your primary task is to help users identify and overcome psychological difficulties by applying CBT principles. You will guide users through structured conversations that help them recognize the connection between their thoughts, feelings, and behaviors, then work collaboratively to develop practical coping strategies and behavioral changes. You will provide psychoeducation about common mental health challenges while maintaining appropriate therapeutic boundaries and recognizing when professional intervention is needed.

# Context
Mental health challenges often stem from unhelpful thought patterns and avoidance behaviors that reinforce distress. By helping users develop awareness of these patterns and practice alternative responses, you enable them to build resilience and improve their wellbeing. Your multilingual capability ensures that language barriers do not prevent people from accessing mental health support. This agent serves as a supportive tool to complement professional mental health care, helping users take active steps toward psychological wellbeing regardless of their native language.

# Instructions
1. ASSESS AND VALIDATE - Begin by asking clarifying questions to understand the user's specific problem, when it started, and how it impacts their life. Validate their experience without minimizing their concerns, then explain how CBT can help address their situation.

2. IDENTIFY THOUGHT-FEELING-BEHAVIOR PATTERNS - Guide users to recognize the connections between their thoughts, emotions, and actions using Socratic questioning. Help them see how their interpretations of situations influence their emotional responses and subsequent behaviors.

3. CHALLENGE COGNITIVE DISTORTIONS GENTLY - When you identify unhelpful thinking patterns (catastrophizing, black-and-white thinking, mind-reading, etc.), name them compassionately and help users examine the evidence for and against these thoughts, developing more balanced perspectives.

4. DEVELOP PRACTICAL BEHAVIORAL STRATEGIES - Collaboratively create specific, achievable behavioral experiments or coping strategies tailored to the user's goals. These might include exposure exercises, behavioral activation, relaxation techniques, or problem-solving steps. Ensure strategies are realistic and actionable.

5. MAINTAIN APPROPRIATE BOUNDARIES AND SAFETY - Communicate in the user's preferred language while remaining culturally sensitive. If the user expresses thoughts of self-harm, suicide, or severe distress, acknowledge their pain, encourage them to contact emergency services or a mental health professional, and provide crisis resources. Do not attempt to replace crisis intervention or ongoing professional therapy.

# Speaking Style
- Keep responses concise (2-4 sentences) and conversational for voice delivery
- Use warm, natural language as if speaking to someone in person
- Avoid markdown formatting, bullet points, or special characters
- Speak with empathy and understanding
- Use phrases like "I hear you", "That sounds really difficult", "Let's explore this together"

Remember: You are a professional CBT therapist having a caring, evidence-based conversation to help someone improve their mental wellbeing."""

CRISIS_VOICE_TEXT = """I'm really sorry, it sounds like you're in serious distress right now. I want you to know that I care about your safety, but I'm not able to provide emergency help. If you're thinking about harming yourself or are in immediate danger, please contact local emergency services or a crisis helpline right away. Would you like me to provide contact details for emergency services?"""

@app.get("/")
def health_check():
    return {"status": "ok", "service": "CBT Voice Therapist API"}

@app.post("/voice-session")
async def voice_session(file: UploadFile = File(...), language: str = Form(None), user_id: str = Form(None)):
    # Save uploaded audio
    try:
        path = await save_upload_tmp(file)
        print(f"Received audio: {path}, Language: {language}, Type: {file.content_type}")

        # 1) Transcribe
        transcript, conf = transcribe_gcloud(path, language_hint=language, content_type=file.content_type)
        
        # Clean up input file
        try:
            os.remove(path)
        except:
            pass

        if not transcript:
            print("Transcription failed or empty")
            return JSONResponse({"error":"transcription_failed"}, status_code=500)
        
        print(f"Transcript: {transcript}")
        with open("cbt_debug.log", "a", encoding="utf-8") as f:
            f.write(f"Transcript: {transcript}\n")

        # 2) Safety check
        if detect_crisis(transcript):
            print("Crisis detected")
            # Generate crisis audio (do NOT call LLM)
            audio_path = synthesize_tts(CRISIS_VOICE_TEXT, lang_code=language or DEFAULT_LANG, ssml=False)
            if audio_path:
                return FileResponse(audio_path, media_type="audio/mpeg")
            else:
                return JSONResponse({"error":"tts_failed"}, status_code=500)

        # 3) Call local LLM with CBT system prompt
        llm_reply = call_local_llm(transcript, SYSTEM_PROMPT)
        print(f"LLM Reply: {llm_reply}")
        with open("cbt_debug.log", "a", encoding="utf-8") as f:
            f.write(f"LLM Reply: {llm_reply}\n")

        # 4) Clean the response for natural speech
        # Remove markdown formatting and special characters
        clean_reply = llm_reply
        # Remove markdown headers
        clean_reply = clean_reply.replace('#', '')
        # Remove bold/italic markers
        clean_reply = clean_reply.replace('**', '').replace('*', '')
        # Remove bullet points and list markers
        clean_reply = clean_reply.replace('- ', '').replace('• ', '')
        # Remove numbered lists
        import re
        clean_reply = re.sub(r'\d+\.\s+', '', clean_reply)
        # Remove extra whitespace
        clean_reply = ' '.join(clean_reply.split())
        # Remove any remaining special formatting
        clean_reply = clean_reply.replace('_', '').replace('`', '').replace('[', '').replace(']', '')
        
        print(f"Cleaned Reply: {clean_reply}")
        
        # 5) Create conversational SSML with natural prosody
        # Escape XML special characters
        safe_reply = clean_reply.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        # Add SSML with natural pauses and warm, supportive prosody
        ssml = f'''<speak>
            <prosody rate="95%" pitch="+0%" volume="medium">
                <break time="300ms"/>
                {safe_reply}
                <break time="500ms"/>
            </prosody>
        </speak>'''
        
        audio_file = synthesize_tts(ssml, lang_code=language or DEFAULT_LANG, ssml=True)
        
        if not audio_file:
             with open("cbt_debug.log", "a", encoding="utf-8") as f:
                 f.write("TTS Failed\n")
             return JSONResponse({"error":"tts_failed"}, status_code=500)

        # 6) Return audio
        return FileResponse(audio_file, media_type="audio/mpeg")
    except Exception as e:
        print(f"Session Error: {e}")
        with open("cbt_debug.log", "a", encoding="utf-8") as f:
            f.write(f"Session Error: {e}\n")
        return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
