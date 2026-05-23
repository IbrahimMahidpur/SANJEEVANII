from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid, os, aiofiles, requests, tempfile, json, re, logging, traceback
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import texttospeech_v1 as tts

# Import Sanjeevani-style multilingual utilities
from agents.multilingual_utils import enhance_text_for_tts as sanjeevani_enhance
from agents.ssml_generator import SSMLGenerator
from agents.advanced_ssml import generate_advanced_ssml


# Import RAG modules (FAISS-based)
try:
    from rag.retriever_faiss import get_retriever
    RAG_AVAILABLE = True
    print("[OK] RAG system loaded (FAISS)")
except Exception as e:
    RAG_AVAILABLE = False
    print(f"[WARNING] RAG unavailable: {e}")
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
            return "\n\n".join(parts)
    
    _memory_manager_instance = None
    def get_memory_manager():
        global _memory_manager_instance
        if _memory_manager_instance is None:
            _memory_manager_instance = SimpleMemoryManager()
        return _memory_manager_instance
    
    MEMORY_AVAILABLE = True
    print("[OK] Memory system loaded (FAISS)")
except Exception as e:
    MEMORY_AVAILABLE = False
    print(f"[WARNING] Memory unavailable: {e}")
    def get_memory_manager():
        return None

# Import Safety module
try:
    from safety.enhanced_safety import get_safety_checker
    SAFETY_AVAILABLE = True
    print("[OK] Safety system loaded")
except Exception as e:
    SAFETY_AVAILABLE = False
    print(f"[WARNING] Safety unavailable: {e}")
    def get_safety_checker():
        return None

# Import Agent modules
try:
    from agents.analyzer import get_analyzer
    from agents.evidence_agent import get_evidence_collector
    from agents.therapy_response import get_therapy_generator
    AGENTS_AVAILABLE = True
    print("[OK] Agents system loaded")
except Exception as e:
    AGENTS_AVAILABLE = False
    print(f"[WARNING] Agents unavailable: {e}")
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
print("\n" + "="*60)
print(" Initializing CBT Components")
print("="*60)

# Try to load enhanced retriever first (195k chunks), fallback to old one
retriever = None
if RAG_AVAILABLE:
    try:
        from rag.retriever_generated import get_enhanced_retriever
        retriever = get_enhanced_retriever()
        print(f"[OK] Enhanced Retriever: {retriever.index.ntotal:,} chunks loaded")
    except Exception as e:
        print(f"[WARNING] Enhanced retriever unavailable: {e}")
        try:
            retriever = get_retriever()
            print(f"[OK] Fallback Retriever loaded")
        except:
            print(f"[ERROR] All retrievers failed")

memory_manager = get_memory_manager() if MEMORY_AVAILABLE else None
safety_checker = get_safety_checker() if SAFETY_AVAILABLE else None
analyzer = get_analyzer() if AGENTS_AVAILABLE else None
evidence_collector = get_evidence_collector() if AGENTS_AVAILABLE else None
therapy_generator = get_therapy_generator() if AGENTS_AVAILABLE else None

print(f"[OK] Retriever: {retriever is not None}")
print(f"[OK] Memory Manager: {memory_manager is not None}")
print(f"[OK] Safety Checker: {safety_checker is not None}")
print(f"[OK] Analyzer: {analyzer is not None}")
print(f"[OK] Evidence Collector: {evidence_collector is not None}")
print(f"[OK] Therapy Generator: {therapy_generator is not None}")
print("="*60 + "\n")

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
    "en-US": {"name": "en-US-Neural2-D", "gender": tts.SsmlVoiceGender.MALE},  # Neural2 for better quality
    "en-IN": {"name": "en-IN-Neural2-B", "gender": tts.SsmlVoiceGender.MALE},  # Indian English (best for Hinglish)
    "hi-IN": {"name": "hi-IN-Neural2-B", "gender": tts.SsmlVoiceGender.MALE},  # Hindi Neural2
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
        
        # Configure STT with Hindi/Hinglish support
        config = {
            "language_code": "hi-IN",  # Primary: Hindi
            "alternative_language_codes": ["en-IN", "en-US"],  # Fallback: Indian English, US English
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
        
        # Concatenate ALL results, not just the first one
        # Google STT sometimes splits long audio into multiple results
        full_transcript = ""
        total_confidence = 0.0
        
        for result in resp.results:
            if result.alternatives:
                best = result.alternatives[0]
                full_transcript += best.transcript + " "
                total_confidence += best.confidence if hasattr(best, 'confidence') else 1.0
        
        full_transcript = full_transcript.strip()
        avg_confidence = total_confidence / len(resp.results) if resp.results else 0.0
        
        logger.info(f"[STT] Transcript ({len(resp.results)} results): '{full_transcript}' ({avg_confidence:.2%})")
        return full_transcript, avg_confidence
        
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
        audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.MP3, speaking_rate=0.95, pitch=-1.0)
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
    clean = re.sub(r'\d+\.\s+', '', clean)
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
    user_id: str = Form(None),
    emotion: str = Form(None)  # NEW: Emotion data from face detection
):
    """
    Voice therapy session endpoint with emotion-adaptive responses
    """
    try:
        logger.info(f"[Session {session_id}] Voice session started")
        
        # Initialize session if needed
        if memory_manager:
            memory_manager.start_session(session_id, user_id)
        
        # Save audio
        path = await save_upload_tmp(file)
        logger.info(f"[Session {session_id}] Received audio")

        # 1) STT - Transcribe
        logger.info(f"[Session {session_id}] ===== STEP 1: STT =====")
        logger.info(f"[Session {session_id}] Audio file: {path}, size: {os.path.getsize(path)} bytes")
        logger.info(f"[Session {session_id}] Content type: {file.content_type}")
        logger.info(f"[Session {session_id}] Language hint: {language}")
        
        transcript, conf = transcribe_gcloud(path, language_hint=language, content_type=file.content_type)

        try:
            os.remove(path)
        except:
            pass

        if not transcript:
            logger.error(f"[Session {session_id}] STT FAILED - No transcript!")
            return JSONResponse({"error":"transcription_failed"}, status_code=500)
        
        logger.info(f"[Session {session_id}] ✓ STT SUCCESS")
        logger.info(f"[Session {session_id}] Transcript: '{transcript}' (confidence: {conf:.2%})")
        
        # Parse emotion data from frontend
        emotion_data = None
        if emotion:
            try:
                import json
                emotion_data = json.loads(emotion)
                logger.info(f"[Session {session_id}] Emotion: {emotion_data.get('emotion')} ({emotion_data.get('confidence', 0):.0%})")
            except Exception as e:
                logger.warning(f"[Session {session_id}] Failed to parse emotion: {e}")
                emotion_data = None

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
            logger.info(f"[Session {session_id}] ===== STEP 6: LLM GENERATION =====")
            logger.info(f"[Session {session_id}] User input: '{transcript}'")
            logger.info(f"[Session {session_id}] Analysis: {analysis.get('emotions', [])} emotions detected")
            logger.info(f"[Session {session_id}] Evidence: {len(evidence.get('techniques', []))} techniques retrieved")
            
            therapy_response = therapy_generator.generate(
                user_input=transcript,
                analysis=analysis,
                evidence=evidence,
                session_memory=memory_context.split('\n\n')[0] if '\n\n' in memory_context else "",
                user_memory=memory_context.split('\n\n')[1] if '\n\n' in memory_context else "",
                emotion_data=emotion_data  # NEW: Pass visual context
            )
            
            logger.info(f"[Session {session_id}] ✓ LLM SUCCESS")
            logger.info(f"[Session {session_id}] Response length: {len(therapy_response)} chars")
            logger.info(f"[Session {session_id}] Response preview: '{therapy_response[:100]}...'")
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


        # 8) Enhance text using Sanjeevani's multilingual logic
        enhanced_text, optimal_lang = sanjeevani_enhance(therapy_response, language)




        # 9) Generate ADVANCED SSML with Google Cloud best practices
        logger.info(f"[Session {session_id}] ===== STEP 9: SSML GENERATION =====")
        logger.info(f"[Session {session_id}] Enhanced text: '{enhanced_text[:100]}...'")
        logger.info(f"[Session {session_id}] Optimal lang: {optimal_lang}")
        
        # SAFETY: Use original response if enhanced_text is empty
        final_text = enhanced_text if enhanced_text and len(enhanced_text.strip()) > 0 else therapy_response
        logger.info(f"[Session {session_id}] Final text length: {len(final_text)} chars")
        
        # Use BASIC SSML with NATURAL rate for smooth, flowing Hinglish
        basic_ssml = f"""<speak>
<prosody rate="105%" pitch="-0.5st">
{final_text}
</prosody>
</speak>"""
        
        logger.info(f"[Session {session_id}] ✓ Basic SSML generated: {len(basic_ssml)} chars")
        logger.info(f"[Session {session_id}] Original text length: {len(therapy_response)} chars")
        logger.info(f"[Session {session_id}] Enhanced text length: {len(enhanced_text)} chars")

        # 10) TTS - Use en-IN (working voice)
        logger.info(f"[Session {session_id}] ===== STEP 10: TTS =====")
        logger.info(f"[Session {session_id}] Using TTS lang: {optimal_lang}")
        
        audio_file = synthesize_tts(basic_ssml, lang_code=optimal_lang if "optimal_lang" in locals() else (language or DEFAULT_LANG), ssml=True)
        
        if not audio_file:
            logger.error(f"[Session {session_id}] ✗ TTS FAILED - No audio file generated!")
            return JSONResponse({"error":"tts_failed"}, status_code=500)
        
        logger.info(f"[Session {session_id}] ✓ TTS SUCCESS - Audio file: {audio_file}")
        logger.info(f"[Session {session_id}] Audio file size: {os.path.getsize(audio_file)} bytes")
        logger.info(f"[Session {session_id}] [OK] Complete")
        return FileResponse(audio_file, media_type="audio/mpeg")
        
    except Exception as e:
        logger.error(f"Session Error: {e}\n{traceback.format_exc()}")
        return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
