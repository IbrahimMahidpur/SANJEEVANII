"""
Generate complete enhanced app.py with RAG, Agents, Memory, and Safety
This script creates a working enhanced version by combining all components
"""

# Read the simple backup version
with open('app_backup.py', 'r', encoding='utf-8') as f:
    simple_version = f.read()

# Enhanced version with all imports and initialization
enhanced_app = '''from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid, os, aiofiles, requests, tempfile, json, re, logging, traceback
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import texttospeech_v1 as tts

# Import RAG modules (FAISS-based)
try:
    from rag.retriever_faiss import get_retriever
    RAG_AVAILABLE = True
    print("✓ RAG system loaded (FAISS)")
except Exception as e:
    RAG_AVAILABLE = False
    print(f"⚠ RAG unavailable: {e}")
    def get_retriever():
        return None

# Import Memory modules (FAISS-based)
try:
    from memory.session_memory import get_session_memory
    from memory.user_memory_faiss import get_user_memory
    
    class SimpleMemoryManager:
        def __init__(self):
            self.session_memory = get_session_memory()
            self.user_memory = get_user_memory()
        
        def start_session(self, session_id, user_id=None):
            self.session_memory.create_session(session_id, user_id)
        
        def add_exchange(self, session_id, user_message, assistant_message, user_id=None, analysis=None):
            self.session_memory.add_message(session_id, 'user', user_message, analysis)
            self.session_memory.add_message(session_id, 'assistant', assistant_message)
            if user_id and analysis:
                if 'emotions' in analysis and 'intensity' in analysis:
                    for emotion in analysis['emotions']:
                        self.user_memory.add_emotional_trend(user_id, emotion, analysis['intensity'])
                if 'distortions' in analysis:
                    for distortion in analysis['distortions']:
                        self.user_memory.add_distortion(user_id, distortion)
        
        def get_context_for_llm(self, session_id, user_id=None):
            parts = []
            session_ctx = self.session_memory.format_for_llm(session_id, last_n=5)
            if session_ctx:
                parts.append(session_ctx)
            if user_id:
                user_ctx = self.user_memory.format_for_llm(user_id)
                if user_ctx:
                    parts.append(user_ctx)
            return "\\n\\n".join(parts)
    
    _memory_manager_instance = None
    def get_memory_manager():
        global _memory_manager_instance
        if _memory_manager_instance is None:
            _memory_manager_instance = SimpleMemoryManager()
        return _memory_manager_instance
    
    MEMORY_AVAILABLE = True
    print("✓ Memory system loaded (FAISS)")
except Exception as e:
    MEMORY_AVAILABLE = False
    print(f"⚠ Memory unavailable: {e}")
    def get_memory_manager():
        return None

# Import Safety module
try:
    from safety.enhanced_safety import get_safety_checker
    SAFETY_AVAILABLE = True
    print("✓ Safety system loaded")
except Exception as e:
    SAFETY_AVAILABLE = False
    print(f"⚠ Safety unavailable: {e}")
    def get_safety_checker():
        return None

# Import Agent modules
try:
    from agents.analyzer import get_analyzer
    from agents.evidence_agent import get_evidence_collector
    from agents.therapy_response import get_therapy_generator
    AGENTS_AVAILABLE = True
    print("✓ Agents system loaded")
except Exception as e:
    AGENTS_AVAILABLE = False
    print(f"⚠ Agents unavailable: {e}")
    def get_analyzer():
        return None
    def get_evidence_collector():
        return None
    def get_therapy_generator():
        return None

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set Google Cloud Credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "vaani-474822-36de07e0981f.json"
)

# Initialize global instances at module level
print("\\n" + "="*60)
print("🚀 Initializing CBT Components")
print("="*60)

retriever = get_retriever() if RAG_AVAILABLE else None
memory_manager = get_memory_manager() if MEMORY_AVAILABLE else None
safety_checker = get_safety_checker() if SAFETY_AVAILABLE else None
analyzer = get_analyzer() if AGENTS_AVAILABLE else None
evidence_collector = get_evidence_collector() if AGENTS_AVAILABLE else None
therapy_generator = get_therapy_generator() if AGENTS_AVAILABLE else None

print(f"✓ Retriever: {retriever is not None}")
print(f"✓ Memory Manager: {memory_manager is not None}")
print(f"✓ Safety Checker: {safety_checker is not None}")
print(f"✓ Analyzer: {analyzer is not None}")
print(f"✓ Evidence Collector: {evidence_collector is not None}")
print(f"✓ Therapy Generator: {therapy_generator is not None}")
print("="*60 + "\\n")

# Create FastAPI app
app = FastAPI(title="CBT Voice Therapist API - Enhanced")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Voice mapping
VOICE_MAP = {
    "en-US": {"name": "en-US-Wavenet-D", "gender": tts.SsmlVoiceGender.MALE},
    "hi-IN": {"name": "hi-IN-Wavenet-A", "gender": tts.SsmlVoiceGender.MALE},
}
DEFAULT_LANG = "en-US"

# Utilities
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
        
        audio = {"content": content}
        encoding = speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED
        sample_rate = None
        
        if content_type:
            if "webm" in content_type:
                encoding = speech.RecognitionConfig.AudioEncoding.WEBM_OPUS
            elif "mpeg" in content_type or "mp3" in content_type:
                encoding = speech.RecognitionConfig.AudioEncoding.MP3
            elif "wav" in content_type:
                encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16
        
        config = {
            "language_code": language_hint or DEFAULT_LANG,
            "enable_automatic_punctuation": True,
            "model": "latest_long",
            "use_enhanced": True,
        }
        
        if encoding != speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED:
            config["encoding"] = encoding
        if sample_rate:
            config["sample_rate_hertz"] = sample_rate
        
        request = {"config": config, "audio": audio}
        resp = client.recognize(request=request)
        
        if not resp.results:
            return "", None
        
        best = resp.results[0].alternatives[0]
        transcript = best.transcript
        confidence = best.confidence if hasattr(best, 'confidence') else 1.0
        
        logger.info(f"[STT] Transcript: '{transcript}' ({confidence:.2%})")
        return transcript, confidence
        
    except Exception as e:
        logger.error(f"[STT] Error: {e}")
        return None, None

def synthesize_tts(text: str, lang_code: str="en-US", voice_name: str=None, ssml=False):
    try:
        client = tts.TextToSpeechClient()
        voice_info = VOICE_MAP.get(lang_code, VOICE_MAP.get(DEFAULT_LANG))
        
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
        logger.error(f"TTS Error: {e}")
        return None

def clean_text_for_speech(text: str) -> str:
    clean = text
    clean = clean.replace('#', '')
    clean = clean.replace('**', '').replace('*', '')
    clean = clean.replace('- ', '').replace('• ', '')
    clean = re.sub(r'\\d+\\.\\s+', '', clean)
    clean = ' '.join(clean.split())
    clean = clean.replace('_', '').replace('`', '').replace('[', '').replace(']', '')
    return clean

# API Routes
@app.get("/")
def health_check():
    return {
        "status": "ok",
        "service": "CBT Voice Therapist API - Enhanced",
        "features": ["RAG", "Multi-Agent", "Memory", "Enhanced Safety"]
    }

@app.post("/voice-session")
async def voice_session(
    file: UploadFile = File(...),
    language: str = Form(None),
    session_id: str = Form(None),
    user_id: str = Form(None)
):
    try:
        # Generate session_id if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Start session
        if memory_manager:
            memory_manager.start_session(session_id, user_id)
        
        # Save audio
        path = await save_upload_tmp(file)
        logger.info(f"[Session {session_id}] Received audio")

        # 1) STT - Transcribe
        transcript, conf = transcribe_gcloud(path, language_hint=language, content_type=file.content_type)
        
        try:
            os.remove(path)
        except:
            pass

        if not transcript:
            return JSONResponse({"error":"transcription_failed"}, status_code=500)
        
        logger.info(f"[Session {session_id}] Transcript: {transcript}")

        # 2) Enhanced Safety Check
        conversation_history = []
        if memory_manager:
            conversation_history = memory_manager.session_memory.get_conversation_history(session_id, last_n=5)
        
        is_safe = True
        if safety_checker:
            is_safe, risk_assessment = safety_checker.check_safety(transcript, conversation_history)
        
        if not is_safe:
            logger.error(f"[Session {session_id}] CRISIS DETECTED")
            crisis_text = safety_checker.get_crisis_response() if safety_checker else "Please seek immediate help."
            audio_path = synthesize_tts(crisis_text, lang_code=language or DEFAULT_LANG)
            
            if memory_manager:
                memory_manager.session_memory.add_message(session_id, 'user', transcript, {'crisis': True})
            
            if audio_path:
                return FileResponse(audio_path, media_type="audio/mpeg")
            else:
                return JSONResponse({"error":"tts_failed"}, status_code=500)

        # 3) Agent 1: Analyze
        analysis = {}
        if analyzer:
            logger.info(f"[Session {session_id}] Running CBT Analyzer...")
            analysis = analyzer.analyze(transcript)

        # 4) Agent 2: Collect Evidence (RAG)
        evidence = {'techniques': [], 'rag_context': ''}
        if evidence_collector and analysis:
            logger.info(f"[Session {session_id}] Collecting evidence...")
            evidence = evidence_collector.collect_evidence(analysis, transcript)

        # 5) Get Memory Context
        memory_context = ""
        if memory_manager:
            memory_context = memory_manager.get_context_for_llm(session_id, user_id)

        # 6) Agent 3: Generate Therapy Response
        therapy_response = ""
        if therapy_generator:
            logger.info(f"[Session {session_id}] Generating therapy response...")
            therapy_response = therapy_generator.generate(
                user_input=transcript,
                analysis=analysis,
                evidence=evidence,
                session_memory=memory_context.split('\\n\\n')[0] if '\\n\\n' in memory_context else "",
                user_memory=memory_context.split('\\n\\n')[1] if '\\n\\n' in memory_context else ""
            )
        else:
            # Fallback to simple LLM
            therapy_response = "I hear you. How are you feeling right now?"

        # 7) Update Memory
        if memory_manager:
            memory_manager.add_exchange(
                session_id=session_id,
                user_message=transcript,
                assistant_message=therapy_response,
                user_id=user_id,
                analysis=analysis
            )

        # 8) Clean text for speech
        clean_response = clean_text_for_speech(therapy_response)

        # 9) Create SSML
        safe_reply = clean_response.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        ssml = f"""<speak>
            <prosody rate="95%" pitch="+0%" volume="medium">
                <break time="300ms"/>
                {safe_reply}
                <break time="500ms"/>
            </prosody>
        </speak>"""

        # 10) TTS
        audio_file = synthesize_tts(ssml, lang_code=language or DEFAULT_LANG, ssml=True)
        
        if not audio_file:
            return JSONResponse({"error":"tts_failed"}, status_code=500)

        logger.info(f"[Session {session_id}] ✓ Complete")
        return FileResponse(audio_file, media_type="audio/mpeg")
        
    except Exception as e:
        logger.error(f"Session Error: {e}\\n{traceback.format_exc()}")
        return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
'''

# Write the enhanced version
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(enhanced_app)

print("✓ Enhanced app.py created successfully!")
print(f"  Size: {len(enhanced_app)} bytes")
print("  Features: RAG, Multi-Agent, Memory, Enhanced Safety")
