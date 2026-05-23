"""
CLI Application for Text-to-Speech (TTS) and Speech-to-Text (STT) integration with Language Learning Models (LLM).

This module uses asyncio for asynchronous operations, threading for parallel task execution, and various
third-party libraries for audio processing and command-line interaction.
"""

import asyncio
import json
import logging
import os
import os.path
import re
import time
import tempfile
import traceback
from json import loads
from pathlib import Path
from threading import Thread
from typing import Optional

import click
import pygame.mixer
import websockets
from colorama import Fore, Style, init
from . import audio as audio_module

from . import __version__
from .audio import AudioIO
from .models import LLM, STT, TTS
from .settings import default_config
from .utils import ThreadSafeState, deep_merge_dicts, logger, print_system_message

logging.getLogger("TTS").setLevel(logging.ERROR)

# Initialize pygame mixer with dummy audio driver to prevent local audio playback
# All audio playback is handled by TalkingHead avatar for lip-sync
try:
    os.environ['SDL_AUDIODRIVER'] = 'dummy'  # No audio output from Python
    pygame.mixer.init()
    logger.info("[Audio] Dummy audio driver enabled - no local playback")
except Exception:
    # Fallback: init normally but audio playback calls are already disabled
    pygame.mixer.init()
    logger.warning("[Audio] Using default audio driver (playback disabled in code)")


async def notify_talkinghead(wav_path: str):
    """
    Send audio file notification to TalkingHead via WebSocket bridge.
    
    Args:
        wav_path: Full path to the generated WAV file.
    """
    # Get the root directory (parent of june_va)
    root_dir = Path(__file__).parent.parent.parent
    shared_audio_dir = root_dir / "shared_audio"
    
    # Copy file to shared_audio if it's not already there
    wav_file = Path(wav_path)
    if not wav_file.exists():
        logger.warning(f"[Bridge] WAV file not found: {wav_path}")
        return
    
    # Generate filename for shared_audio
    shared_wav_path = shared_audio_dir / wav_file.name
    
    # Copy to shared directory if needed
    if wav_file.parent != shared_audio_dir:
        try:
            shared_audio_dir.mkdir(exist_ok=True)
            import shutil
            shutil.copy2(wav_file, shared_wav_path)
            logger.debug(f"[Bridge] Copied audio to shared directory: {shared_wav_path.name}")
        except Exception as e:
            logger.error(f"[Bridge] Failed to copy audio file: {e}")
            return
    
    # Create audio URL
    audio_url = f"http://localhost:8001/{shared_wav_path.name}"
    
    try:
        # Connect without timeout parameter to avoid compatibility issues
        async with websockets.connect("ws://localhost:8765") as ws:
            # Include a timestamp and source so clients can ignore stale messages
            msg = json.dumps({
                "type": "tts_done",
                "audioUrl": audio_url,
                "source": "june_va",
                "timestamp": int(time.time() * 1000)
            })
            await ws.send(msg)
            logger.info(f"[Bridge] ✅ Sent audio URL to TalkingHead: {audio_url}")
    except (websockets.exceptions.WebSocketException, ConnectionRefusedError) as e:
        # Silently ignore if bridge is not running - don't spam console
        logger.debug(f"[Bridge] WebSocket bridge not available: {e}")
    except Exception as e:
        logger.warning(f"[Bridge] Failed to notify TalkingHead: {e}")



def notify_talkinghead_sync(wav_path: str):
    """
    Synchronous wrapper for notify_talkinghead to use in non-async contexts.
    
    Args:
        wav_path: Full path to the generated WAV file.
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're in an async context, schedule as a task
            asyncio.create_task(notify_talkinghead(wav_path))
        else:
            # Otherwise run in new event loop
            asyncio.run(notify_talkinghead(wav_path))
    except Exception as e:
        logger.debug(f"[Bridge] Could not notify TalkingHead: {e}")


def validate_gcloud_credentials_and_apis(config: dict):
    """
    Validate Google Cloud credentials and API enablement at startup.
    
    Args:
        config: The application configuration dictionary.
        
    Raises:
        RuntimeError: If credentials are invalid or APIs are not enabled.
    """
    stt_config = config.get("stt", {})
    tts_config = config.get("tts", {})
    
    # Check if using Google Cloud providers
    uses_gcloud_stt = stt_config.get("model") == "google"
    uses_gcloud_tts = tts_config.get("model") == "google"
    
    if not (uses_gcloud_stt or uses_gcloud_tts):
        return  # No validation needed for non-Google providers
    
    # Check credentials path
    stt_creds = stt_config.get("generation_args", {}).get("credentials")
    tts_creds = tts_config.get("generation_args", {}).get("credentials")
    
    # Check GOOGLE_APPLICATION_CREDENTIALS env var
    env_creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    
    if not (stt_creds or tts_creds or env_creds):
        raise RuntimeError(
            "Google Cloud credentials not found.\n"
            "Please either:\n"
            "  1. Set GOOGLE_APPLICATION_CREDENTIALS environment variable, or\n"
            "  2. Provide 'credentials' path in config under stt/tts generation_args\n"
            "Download your service account JSON from:\n"
            "  https://console.cloud.google.com/iam-admin/serviceaccounts"
        )
    
    # Validate credentials file exists
    creds_path = stt_creds or tts_creds or env_creds
    if creds_path and not os.path.exists(creds_path):
        raise RuntimeError(
            f"Credentials file not found: {creds_path}\n"
            "Please check the path and ensure the file exists."
        )
    
    # Test API access by attempting to create clients
    try:
        if uses_gcloud_tts:
            from google.cloud import texttospeech
            tts_client = texttospeech.TextToSpeechClient()
            # Test API by listing voices (lightweight operation)
            tts_client.list_voices()
            logger.info("✓ Google Cloud Text-to-Speech API validated")
            
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg or "SERVICE_DISABLED" in error_msg:
            raise RuntimeError(
                "Google Cloud Text-to-Speech API is not enabled.\n"
                "Please enable it at:\n"
                "  https://console.developers.google.com/apis/api/texttospeech.googleapis.com/overview\n"
                "Also ensure billing is enabled for your project."
            )
        elif "401" in error_msg or "UNAUTHENTICATED" in error_msg:
            raise RuntimeError(
                "Invalid Google Cloud credentials.\n"
                "Please check your service account JSON file."
            )
        else:
            raise RuntimeError(f"Google Cloud TTS validation failed: {error_msg}")
    
    try:
        if uses_gcloud_stt:
            from google.cloud import speech_v1p1beta1 as speech
            stt_client = speech.SpeechClient()
            logger.info("✓ Google Cloud Speech-to-Text API validated")
            
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg or "SERVICE_DISABLED" in error_msg:
            raise RuntimeError(
                "Google Cloud Speech-to-Text API is not enabled.\n"
                "Please enable it at:\n"
                "  https://console.developers.google.com/apis/api/speech.googleapis.com/overview\n"
                "Also ensure billing is enabled for your project."
            )
        elif "401" in error_msg or "UNAUTHENTICATED" in error_msg:
            raise RuntimeError(
                "Invalid Google Cloud credentials.\n"
                "Please check your service account JSON file."
            )
        else:
            raise RuntimeError(f"Google Cloud STT validation failed: {error_msg}")


class AppState:
    """Enumeration for application states."""

    READY_FOR_INPUT = 0  # Ready to take user input
    LLM_RESPONSE_GENERATED = 1


current_app_state = ThreadSafeState(AppState.READY_FOR_INPUT)
tts_generation_error = ThreadSafeState(False)
shutdown_event = asyncio.Event()


async def _clear_queue(queue: asyncio.Queue[str]):
    """
    Clear all items from the asyncio queue.

    Args:
        queue: The queue to be cleared.
    """
    while not queue.empty():
        _ = await queue.get()
        queue.task_done()


async def _real_main(**kwargs):
    """
    Main function to set up models, process configurations, and handle producer-consumer tasks.

    Args:
        **kwargs: Arbitrary keyword arguments including config file.
    """
    # If a config file was passed via --config, use it. Otherwise attempt to
    # load a default `config.json` from the repository root so users can run
    # the CLI without explicitly passing -c.
    if kwargs.get("config"):
        try:
            user_config = loads(kwargs["config"].read())
        except Exception:
            user_config = {}
    else:
        # Look for a project-level config.json (three levels up from this file)
        default_cfg_path = Path(__file__).parent.parent.parent / "config.json"
        if default_cfg_path.exists():
            try:
                with open(default_cfg_path, "r", encoding="utf-8") as f:
                    user_config = loads(f.read())
                    logger.debug(f"Loaded project config from {default_cfg_path}")
            except Exception:
                user_config = {}
        else:
            user_config = {}
    config = deep_merge_dicts(default_config, user_config)
    # If GOOGLE_APPLICATION_CREDENTIALS is not set in the environment,
    # prefer the credentials path specified in the merged config (stt/tts generation_args).
    # This makes it easier to run the CLI without setting an env var separately.
    try:
        if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            stt_creds = config.get("stt", {}).get("generation_args", {}).get("credentials")
            tts_creds = config.get("tts", {}).get("generation_args", {}).get("credentials")
            creds_path = stt_creds or tts_creds
            if creds_path:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
                logger.debug(f"Set GOOGLE_APPLICATION_CREDENTIALS from config: {creds_path}")
    except Exception:
        # Non-fatal: if anything goes wrong here, validation will surface the issue.
        logger.debug("Could not set GOOGLE_APPLICATION_CREDENTIALS from config; continuing to validation")

    # Validate Google Cloud credentials and APIs before proceeding
    try:
        validate_gcloud_credentials_and_apis(config)
    except RuntimeError as e:
        print_system_message(str(e), color=Fore.RED, log_level=logging.ERROR)
        return 3

    llm_config = config["llm"]
    stt_config = config.get("stt") or {}
    tts_config = config.get("tts") or {}

    if stt_config:
        try:
            import pyaudio
        except ImportError:
            print_system_message(
                (
                    "PyAudio not installed. Please install PyAudio for speech recognition and audio synthesis to "
                    "work."
                ),
                color=Fore.RED,
                log_level=logging.ERROR,
            )
            return 1

    llm_model = LLM(**llm_config)

    if not llm_model.exists():
        print_system_message(f"Invalid ollama model: {llm_model.model_id}", color=Fore.RED, log_level=logging.ERROR)
        return 2

    if llm_config.get("disable_chat_history"):
        print_system_message(
            "Chat history is currently disabled. The conversation may not be fully interactive, as the "
            "assistant will not retain previous context. Each interaction will be treated independently.",
            color=Fore.YELLOW,
        )

    if not llm_config.get("system_prompt"):
        print_system_message("No system prompt provided.")

    stt_model = STT(**stt_config) if stt_config else None
    tts_model = TTS(**tts_config) if tts_config else None

    text_queue = asyncio.Queue()
    detected_lang_holder = {'language': None}  # Shared dict for detected language

    # Start a background thread that listens on the bridge for control messages
    # (pause_capture / resume_capture). This allows the frontend to instruct
    # June VA to pause microphone capture while the avatar speaks.
    def _bridge_listener_thread():
        async def bridge_listener():
            import json
            import asyncio
            import websockets
            uri = "ws://localhost:8765"
            while not shutdown_event.is_set():
                try:
                    async with websockets.connect(uri) as ws:
                        # Keep connection open and listen for commands
                        async for msg in ws:
                            try:
                                data = json.loads(msg)
                            except Exception:
                                continue
                            t = data.get('type')
                            if t == 'pause_capture':
                                try:
                                    audio_module.pause_capture_global()
                                    logger.info('[BridgeListener] Paused capture from bridge')
                                except Exception:
                                    logger.exception('Failed to pause capture')
                            elif t == 'resume_capture':
                                try:
                                    audio_module.resume_capture_global()
                                    logger.info('[BridgeListener] Resumed capture from bridge')
                                except Exception:
                                    logger.exception('Failed to resume capture')
                except Exception as e:
                    logger.debug('[BridgeListener] Connection error, retrying in 1s: %s', e)
                    try:
                        await asyncio.sleep(1)
                    except Exception:
                        pass

        try:
            asyncio.run(bridge_listener())
        except Exception:
            logger.exception('Bridge listener thread terminated unexpectedly')

    t_listener = Thread(target=_bridge_listener_thread, daemon=True)
    t_listener.start()

    # Run consumer task in separate thread
    thread = Thread(target=run_async_tasks, args=(text_queue, tts_model, detected_lang_holder))
    thread.start()

    try:
        producer(text_queue, llm_model, stt_model, detected_lang_holder)
    except KeyboardInterrupt:
        ...
    finally:
        shutdown_event.set()
        thread.join()
        await _clear_queue(text_queue)
        await text_queue.join()

        # Attempt to stop playback and remove any generated tts files if safe.
        if tts_model:
            try:
                # No local playback happening, so just clean up files
                # Wait briefly for TalkingHead to finish playing
                await asyncio.sleep(0.5)

                # Collect candidate files to remove: model.file_path and any generated files (Google TTS)
                candidates = set()
                if hasattr(tts_model, "file_path") and tts_model.file_path:
                    candidates.add(tts_model.file_path)
                if hasattr(tts_model, "_generated_files"):
                    for p in getattr(tts_model, "_generated_files", []):
                        candidates.add(p)

                for path in list(candidates):
                    if not os.path.exists(path):
                        continue
                    try:
                        os.remove(path)
                    except PermissionError:
                        print_system_message(
                            f"Could not remove {path} because it is in use. Please remove it manually.",
                            color=Fore.YELLOW,
                            log_level=logging.WARNING,
                        )
                    except Exception:
                        logger.exception("Failed to remove TTS file %s", path)
            except Exception:
                logger.exception("Unexpected error during shutdown file cleanup")


async def consumer(text_queue: asyncio.Queue[str], tts_model: Optional[TTS], detected_lang_holder: dict):
    """
    Consumer task to process text from the queue and generate TTS output.

    Args:
        text_queue: Queue containing text to process.
        tts_model: Text-to-Speech model for generating audio.
        detected_lang_holder: Dict containing detected language for TTS.
    """
    def clean_text_for_tts(text: str) -> str:
        """Enhanced text cleaning and language optimization for TTS."""
        try:
            from .multilingual_utils import enhance_text_for_tts
            from .language_detector import LanguageDetector
            
            # Get detected language from STT (user's input language)
            stt_detected_lang = detected_lang_holder.get('language')
            
            # Detect language of the response text itself
            response_lang, _ = LanguageDetector.detect_language(text)
            
            # Log detection for debugging
            logger.info(f"STT detected: {stt_detected_lang}, Response detected: {response_lang}")
            
            # IMPORTANT: Prioritize INPUT language for voice selection
            # If user spoke Hindi, use Hindi voice even if response is Hinglish
            optimal_tts_lang = stt_detected_lang or response_lang or "en-IN"
            
            # Normalize language code
            if optimal_tts_lang:
                optimal_tts_lang = optimal_tts_lang.replace('_', '-').upper()
            
            # For Hinglish detection: If STT detected Hindi but response is English,
            # check if response has Hindi words - if yes, keep Hindi voice
            if optimal_tts_lang and optimal_tts_lang.startswith('HI'):
                logger.info(f"✓ Input was Hindi - using Hindi voice for response")
            elif optimal_tts_lang and optimal_tts_lang.startswith('EN'):
                # Check if response has Hindi words despite being detected as English
                # STRICT THRESHOLD: Require 5+ Hindi words to switch to Hindi voice
                hindi_word_count = LanguageDetector.count_hindi_words(text)
                if hindi_word_count >= 5:
                    logger.info(f"✓ Response has {hindi_word_count} Hindi words - using Hindi voice")
                    optimal_tts_lang = "HI-IN"
            
            # Enhanced text processing
            enhanced_text, _ = enhance_text_for_tts(text, optimal_tts_lang)
            
            # Store optimal language for TTS to use
            detected_lang_holder['optimal_tts_lang'] = optimal_tts_lang
            
            logger.info(f"🎤 TTS Voice: {optimal_tts_lang} for text: '{text[:50]}...'")
            logger.debug(f"Text enhanced: '{text[:50]}...' → '{enhanced_text[:50]}...'")
            
            return enhanced_text
        except Exception as e:
            logger.warning(f"Enhanced text processing failed: {e}")
            # Fallback to legacy processing
            return _legacy_clean_text_for_tts(text)
    
    def _legacy_clean_text_for_tts(text: str) -> str:
        """Legacy fallback: Remove markdown formatting symbols (*, **, _, __, #) but keep the text."""
        import re
        
        # Remove markdown bold (**text** becomes text)
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        # Remove markdown italic (*text* becomes text)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        # Remove underscores used for formatting
        text = re.sub(r'__(.+?)__', r'\1', text)
        text = re.sub(r'_(.+?)_', r'\1', text)
        # Remove markdown headers (### Header becomes Header)
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        # Remove markdown list markers (* - 1. 2.)
        text = re.sub(r'^\s*[\*\-\d+\.]\s+', '', text, flags=re.MULTILINE)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Fallback: PRIORITIZE STT detected language (input language)
        try:
            from .language_detector import LanguageDetector
            
            # Get STT detected language (user's input language)
            stt_lang = detected_lang_holder.get('language', 'en-IN')
            
            # Use STT language as primary choice
            optimal_tts_lang = stt_lang
            
            # If STT language not available, detect from response text
            if not optimal_tts_lang or optimal_tts_lang == 'unknown':
                response_lang, _ = LanguageDetector.detect_language(text)
                optimal_tts_lang = response_lang
            
            # Normalize
            if optimal_tts_lang:
                optimal_tts_lang = optimal_tts_lang.replace('_', '-').upper()
            
            detected_lang_holder['optimal_tts_lang'] = optimal_tts_lang
            logger.info(f"Fallback TTS voice: {optimal_tts_lang} (from STT input)")
        except Exception:
            # Last resort: use STT detected language or default
            detected_lang_holder['optimal_tts_lang'] = detected_lang_holder.get('language', 'en-IN')
        
        return text
    
    # Try enhanced processing, fall back to legacy if needed
    def process_text_for_tts(text: str) -> str:
        try:
            return clean_text_for_tts(text)
        except Exception as e:
            logger.warning(f"Enhanced text processing failed, using legacy: {e}")
            return _legacy_clean_text_for_tts(text)
    
    with AudioIO() as audio_io:
        while not shutdown_event.is_set():
            try:
                synthesis = None
                text_buffer = text_queue.get_nowait()
                
                # Clean text for TTS using enhanced processing
                clean_text = process_text_for_tts(text_buffer)

                if tts_model:
                    try:
                        # No need to check pygame mixer since we're not playing locally
                        # All audio handled by TalkingHead

                        # Use optimal TTS language determined by text processing
                        optimal_tts_lang = detected_lang_holder.get('optimal_tts_lang') or detected_lang_holder.get('language')
                        
                        logger.info(f"TTS synthesis: lang={optimal_tts_lang}, text='{clean_text[:50]}...'")
                        synthesis = tts_model.forward(clean_text, language_code=optimal_tts_lang)
                    except Exception as exc:
                        # Capture and log exception details for debugging
                        tts_generation_error.set_value(True)
                        print_system_message(
                            "Text-to-speech generation exception: see logs",
                            color=Fore.YELLOW,
                            log_level=logging.ERROR,
                        )
                        logger.exception("TTS generation failed")

                if synthesis:
                    # No need to wait for pygame mixer since we're not playing locally
                    # All audio is handled by TalkingHead via WebSocket

                    # If the TTS forward returned a file path (e.g., Google TTS), send to TalkingHead
                    if isinstance(synthesis, str):
                        if os.path.exists(synthesis):
                            try:
                                # DISABLED: Let TalkingHead play the audio for lip-sync
                                # audio_io.play_wav(synthesis)
                                
                                # Notify TalkingHead for real-time lip-sync
                                asyncio.create_task(notify_talkinghead(synthesis))
                                logger.info("[Bridge] Audio sent to TalkingHead (not playing locally)")
                            except Exception:
                                tts_generation_error.set_value(True)
                                logger.exception("Failed to notify TalkingHead %s", synthesis)
                        else:
                            # path returned but missing; mark as error
                            tts_generation_error.set_value(True)
                            logger.error("TTS returned path does not exist: %s", synthesis)
                    else:
                        # Assume legacy Coqui path: waveform data that has a synthesizer.save_wav
                        try:
                            # Generate unique filename to avoid permission issues
                            temp_dir = tempfile.gettempdir()
                            timestamp = int(time.time() * 1000)
                            unique_path = os.path.join(temp_dir, f"june_tts_{timestamp}.wav")
                            
                            tts_model.model.synthesizer.save_wav(wav=synthesis, path=unique_path)

                            try:
                                # DISABLED: Let TalkingHead play the audio for lip-sync
                                # audio_io.play_wav(unique_path)
                                
                                # Notify TalkingHead for real-time lip-sync
                                asyncio.create_task(notify_talkinghead(unique_path))
                                logger.info("[Bridge] Audio sent to TalkingHead (not playing locally)")
                                
                                # Note: Don't delete file immediately, TalkingHead needs it
                                # It will be cleaned up later or on next run
                            except Exception:
                                tts_generation_error.set_value(True)
                                logger.exception("Failed to notify TalkingHead %s", unique_path)
                        except Exception:
                            # Could not save/play synthesis
                            tts_generation_error.set_value(True)
                            logger.exception("Failed to save Coqui synthesis")

                text_queue.task_done()
            except asyncio.QueueEmpty:
                # Queue empty - ready for next input
                # No need to wait for pygame mixer since audio plays on TalkingHead
                if current_app_state.get_value() != AppState.READY_FOR_INPUT:
                    current_app_state.set_value(AppState.READY_FOR_INPUT)

                await asyncio.sleep(0.25)


async def start_async_tasks(text_queue: asyncio.Queue[str], tts_model: Optional[TTS], detected_lang_holder: dict):
    """
    Start consumer task for processing text queue.

    Args:
        text_queue: Queue containing text to process.
        tts_model: Text-to-Speech model for generating audio.
        detected_lang_holder: Dict containing detected language.
    """
    consumer_task = asyncio.create_task(consumer(text_queue, tts_model, detected_lang_holder))

    try:
        # Wait until consumer finishes
        await consumer_task
    except asyncio.CancelledError:
        ...


@click.command()
@click.option(
    "-c",
    "--config",
    help="Configuration file.",
    nargs=1,
    required=False,
    type=click.File("r", encoding="utf-8"),
)
@click.option(
    "-v",
    "--verbose",
    help="Verbose mode.",
    is_flag=True,
)
@click.version_option(__version__)
def main(**kwargs):
    """
    Local voice assistant tool.
    """
    if kwargs["verbose"]:
        logger.setLevel(logging.DEBUG)

    asyncio.run(_real_main(**kwargs))


def producer(text_queue: asyncio.Queue[str], llm_model: LLM, stt_model: Optional[STT], detected_lang_holder: dict) -> None:
    """
    Producer task to gather user input, process with LLM, and queue for TTS.

    Args:
        text_queue: Queue to put processed text chunks.
        llm_model: Language Learning Model for processing user input.
        stt_model: Speech-to-Text model for transcribing audio input.
        detected_lang_holder: Dict to store detected language for TTS.
    """
    audio_io = AudioIO()
    min_chunk_size = 10
    splitters = [".", ",", "?", ":", ";"]

    def get_user_input():
        if stt_model:
            audio_data = audio_io.record_audio()

            if audio_data is not None:
                print_system_message("Transcribing audio...")

                result = stt_model.forward(audio_data)
                
                # Handle tuple return (text, language) from Google STT
                if isinstance(result, tuple):
                    transcription, detected_lang = result
                    # Normalize language code to canonical form: en-us or en_us -> en-US
                    def _canonical_lang(code: str):
                        if not code:
                            return None
                        code = code.replace('_', '-').strip()
                        parts = code.split('-')
                        if len(parts) == 1:
                            return parts[0].lower()
                        # language-region -> ll-RR (e.g., en-us -> en-US)
                        lang = parts[0].lower()
                        region = parts[1].upper() if parts[1] else ""
                        return f"{lang}-{region}" if region else lang

                    detected_lang = _canonical_lang(detected_lang)
                    detected_lang_holder['language'] = detected_lang
                    print_system_message(f"Detected language: {detected_lang}", color=Fore.YELLOW)
                else:
                    transcription = result
                    detected_lang_holder['language'] = None
                
                # Debug: show what was transcribed
                if transcription:
                    logger.info(f"Transcription: '{transcription}' (lang: {detected_lang_holder.get('language', 'unknown')})")
                else:
                    logger.warning("Empty transcription received from STT")

                return transcription

        return input(f"{Style.BRIGHT}{Fore.CYAN}[user]>{Style.RESET_ALL} ")

    # Regular expression pattern to match 'quit', 'stop', or 'exit', ignoring case
    exit_pattern = re.compile(r"\b(exit|quit|stop)\b", re.IGNORECASE)

    while True:
        if current_app_state.get_value() != AppState.READY_FOR_INPUT:
            time.sleep(0.25)
            continue

        if tts_generation_error.get_value():
            print_system_message(
                "Some text-to-speech generation failed.",
                color=Fore.YELLOW,
                log_level=logging.WARNING,
            )
            tts_generation_error.set_value(False)

        buffer = []
        user_input = get_user_input()

        if stt_model:
            print(f"{Style.BRIGHT}{Fore.CYAN}[user]>{Style.RESET_ALL} {user_input}")

        if user_input:
            if exit_pattern.search(user_input):
                print_system_message("Exiting...")
                break

            print(f"{Style.BRIGHT}{Fore.GREEN}[assistant]> {Style.NORMAL}", end="", flush=True)

            # Buffer for full response to clean markdown
            full_response = []
            
            for token in llm_model.forward(user_input):
                full_response.append(token)
                
                # Remove only * symbols for display (keep the text)
                # **bold** → bold, *italic* → italic
                display_token = token.replace('*', '')
                print(display_token, end="", flush=True)

                buffer.append(token)

                # Check if buffer is ready to be chunked
                if token == "\n" or (len(buffer) >= min_chunk_size and token in splitters):
                    chunk = "".join(buffer).strip()

                    buffer.clear()

                    if chunk:
                        # Queue this chunk for TTS processing
                        text_queue.put_nowait(chunk)

            # Process any remaining text in buffer
            if buffer:
                chunk = "".join(buffer).strip()

                if chunk:
                    text_queue.put_nowait(chunk)

            current_app_state.set_value(AppState.LLM_RESPONSE_GENERATED)

            print(Style.RESET_ALL)

    audio_io.close()


def run_async_tasks(text_queue: asyncio.Queue[str], tts_model: Optional[TTS], detected_lang_holder: dict):
    """
    Run async tasks in a new event loop for thread safety.

    Args:
        text_queue: Queue to put processed text chunks.
        tts_model: Text-to-Speech model for generating audio.
        detected_lang_holder: Dict containing detected language.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(start_async_tasks(text_queue, tts_model, detected_lang_holder))
    except Exception:
        loop.close()
