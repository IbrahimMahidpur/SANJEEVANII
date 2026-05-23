"""
This module provides a Speech-to-Text (STT) class for transcribing audio data into text using the Transformers library or Google Cloud Speech.
"""

import logging
import warnings
from typing import Dict, Union
import numpy as np

from numpy import ndarray

from ..settings import settings
from .common import BaseModel

logger = logging.getLogger(__name__)


class STT(BaseModel):
    """
    A class for transcribing audio data into text using the Transformers library.

    This class inherits from the BaseModel class and provides a method for running
    the Speech-to-Text model on audio data.

    Args:
        **kwargs: Keyword arguments for initializing the STT model, including optional
            arguments like 'device', 'generation_args', and 'model'.

    Attributes:
        model: An instance of the Transformers pipeline for automatic speech recognition.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        # Support a Google Cloud Speech-to-Text provider when `model` is set to "google".
        if str(self.model_id).lower() in ("google", "gcloud", "google-speech"):
            try:
                from google.oauth2 import service_account
                from google.cloud import speech_v1p1beta1 as speech
            except Exception as exc:  # pragma: no cover - external dependency
                raise RuntimeError("Google Cloud Speech package not installed. Install 'google-cloud-speech'.") from exc

            # Load credentials path from generation_args or environment variable
            cred_path = self.generation_args.get("credentials")
            if not cred_path:
                cred_path = None

            creds = None
            if cred_path:
                creds = service_account.Credentials.from_service_account_file(cred_path)

            # Create the client (will use GOOGLE_APPLICATION_CREDENTIALS if creds is None)
            self._gc_client = speech.SpeechClient(credentials=creds)
            self._gc_speech = speech
            
            # Multilingual config
            self.primary_language = self.generation_args.get("primary_language", "en-US")
            self.alternative_language_codes = self.generation_args.get("alternative_language_codes", [])
            self.sample_rate_hertz = int(self.generation_args.get("sample_rate_hertz", 24000))
            self.enable_automatic_punctuation = bool(self.generation_args.get("enable_automatic_punctuation", True))
            self.use_enhanced = bool(self.generation_args.get("use_enhanced", True))
            self.model_choice = self.generation_args.get("model_choice", "default")
            self.multilang_mode = self.generation_args.get("multilang_mode", "alternative_list")  # "alternative_list" or "auto_detect"
            
            # Speech contexts for better recognition of specific phrases
            self.speech_contexts = self.generation_args.get("speech_contexts", {})
            return

        # Default: Hugging Face pipeline
        with warnings.catch_warnings():
            # Ignore the `resume_download` warning raised by Hugging Face's underlying library
            warnings.simplefilter("ignore", lineno=1132)

            from transformers import pipeline

            self.model = pipeline(
                "automatic-speech-recognition",
                chunk_length_s=10,
                device=self.device,
                model=self.model_id,
                token=settings.HF_TOKEN,
                torch_dtype="auto",
                trust_remote_code=True,
            )

    def _detect_language_from_text(self, text: str) -> str:
        """Detect language from transcript using langdetect. Returns Google language code."""
        try:
            from langdetect import detect_langs
            
            # Check if text contains non-ASCII (likely non-English)
            has_devanagari = any('\u0900' <= c <= '\u097F' for c in text)  # Hindi/Sanskrit
            has_bengali = any('\u0980' <= c <= '\u09FF' for c in text)  # Bengali
            has_tamil = any('\u0B80' <= c <= '\u0BFF' for c in text)  # Tamil
            has_telugu = any('\u0C00' <= c <= '\u0C7F' for c in text)  # Telugu
            
            # If we detect script, immediately return that language
            if has_devanagari:
                logger.info(f"Detected Devanagari script, returning hi-IN")
                return "hi-IN"
            if has_bengali:
                logger.info(f"Detected Bengali script, returning bn-IN")
                return "bn-IN"
            if has_tamil:
                logger.info(f"Detected Tamil script, returning ta-IN")
                return "ta-IN"
            if has_telugu:
                logger.info(f"Detected Telugu script, returning te-IN")
                return "te-IN"
            
            # Fallback to langdetect
            langs = detect_langs(text)
            if langs:
                best = langs[0]
                code = best.lang
                logger.info(f"langdetect detected: {code} (confidence: {best.prob:.2f})")
                
                # Map langdetect codes to Google language codes
                mapping = {
                    "hi": "hi-IN", "en": "en-US", "bn": "bn-IN",
                    "ta": "ta-IN", "te": "te-IN", "mr": "mr-IN",
                    "gu": "gu-IN", "kn": "kn-IN", "ml": "ml-IN",
                    "pa": "pa-IN", "ur": "ur-IN"
                }
                return mapping.get(code, f"{code}-IN")
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            pass
        return self.primary_language

    def forward(self, audio: Dict[str, Union[int, ndarray]]) -> Union[str, tuple]:
        """
        Transcribe audio data into text using the Speech-to-Text model.

        Args:
            audio: A dictionary containing the audio data,
                with a 'sample_rate' key for the sample rate (int) and an 'array' key for the audio array (np.ndarray).

        Returns:
            For Google Cloud STT: tuple of (transcribed_text, detected_language_code)
            For Hugging Face STT: transcribed text string only
        """
        self.detected_language = None  # Store detected language
        # If using Google Cloud Speech client
        if hasattr(self, "_gc_client"):
            # Accept either keys: ('raw', 'sampling_rate') as returned by AudioIO.record_audio
            # or ('array','sample_rate') for transformers pipeline compatibility.
            # Prefer keys produced by AudioIO.record_audio: 'raw' and 'sampling_rate'
            raw = audio.get("raw")
            if raw is None:
                raw = audio.get("array")

            sample_rate = int(audio.get("sampling_rate") or audio.get("sample_rate") or 24000)

            # Convert normalized float32 [-1,1] to int16 PCM
            import numpy as _np

            if raw is None:
                raise ValueError("No audio data provided to STT.forward")

            pcm16 = (_np.asarray(raw) * _np.iinfo(_np.int16).max).astype(_np.int16).tobytes()

            content = pcm16

            # Valid language codes we support - reject anything else
            VALID_LANGS = {'EN-US', 'EN-IN', 'HI-IN', 'BN-IN', 'TA-IN', 'TE-IN', 'MR-IN', 'GU-IN'}
            
            # Strategy for multilingual detection:
            # 1. Try with Hindi as primary first (since user is speaking Hindi/Bengali more often)
            # 2. If no Devanagari/Bengali script found, use English result
            
            recognition_audio = self._gc_speech.RecognitionAudio(content=content)
            
            # Debug: log config
            logger.info(f"STT Config - Mode: {self.multilang_mode}, Alternatives: {self.alternative_language_codes}")
            
            try:
                # Try Hindi first if we have it in alternatives
                best_transcript = ""
                best_lang = self.primary_language
                best_has_script = False
                
                # Attempt 1: Try with Hindi as primary
                if self.alternative_language_codes and 'hi-IN' in self.alternative_language_codes:
                    logger.info("Attempt 1: Trying with Hindi as primary")
                    audio_config_hindi = self._gc_speech.RecognitionConfig(
                        encoding=self._gc_speech.RecognitionConfig.AudioEncoding.LINEAR16,
                        sample_rate_hertz=sample_rate,
                        language_code="hi-IN",
                        enable_automatic_punctuation=self.enable_automatic_punctuation,
                        use_enhanced=self.use_enhanced,
                        model=self.model_choice,
                    )
                    
                    response_hindi = self._gc_client.recognize(config=audio_config_hindi, audio=recognition_audio)
                    
                    if response_hindi.results and response_hindi.results[0].alternatives:
                        transcript_hindi = response_hindi.results[0].alternatives[0].transcript
                        logger.info(f"  Hindi transcript: '{transcript_hindi}'")
                        
                        # Check for Devanagari script
                        has_devanagari = any('\u0900' <= c <= '\u097F' for c in transcript_hindi)
                        if has_devanagari:
                            logger.info(f"  ✓ Found Devanagari script!")
                            best_transcript = transcript_hindi
                            best_lang = "HI-IN"
                            best_has_script = True
                
                # Attempt 2: Try with Bengali if no Hindi script found
                if not best_has_script and self.alternative_language_codes and 'bn-IN' in self.alternative_language_codes:
                    logger.info("Attempt 2: Trying with Bengali as primary")
                    audio_config_bengali = self._gc_speech.RecognitionConfig(
                        encoding=self._gc_speech.RecognitionConfig.AudioEncoding.LINEAR16,
                        sample_rate_hertz=sample_rate,
                        language_code="bn-IN",
                        enable_automatic_punctuation=self.enable_automatic_punctuation,
                        use_enhanced=self.use_enhanced,
                        model=self.model_choice,
                    )
                    
                    response_bengali = self._gc_client.recognize(config=audio_config_bengali, audio=recognition_audio)
                    
                    if response_bengali.results and response_bengali.results[0].alternatives:
                        transcript_bengali = response_bengali.results[0].alternatives[0].transcript
                        logger.info(f"  Bengali transcript: '{transcript_bengali}'")
                        
                        # Check for Bengali script
                        has_bengali = any('\u0980' <= c <= '\u09FF' for c in transcript_bengali)
                        if has_bengali:
                            logger.info(f"  ✓ Found Bengali script!")
                            best_transcript = transcript_bengali
                            best_lang = "BN-IN"
                            best_has_script = True
                
                # Attempt 3: Try with English if no Indian script found
                if not best_has_script:
                    logger.info("Attempt 3: Trying with English as primary")
                    audio_config_english = self._gc_speech.RecognitionConfig(
                        encoding=self._gc_speech.RecognitionConfig.AudioEncoding.LINEAR16,
                        sample_rate_hertz=sample_rate,
                        language_code=self.primary_language,
                        enable_automatic_punctuation=self.enable_automatic_punctuation,
                        use_enhanced=self.use_enhanced,
                        model=self.model_choice,
                    )
                    
                    response_english = self._gc_client.recognize(config=audio_config_english, audio=recognition_audio)
                    
                    if response_english.results and response_english.results[0].alternatives:
                        transcript_english = response_english.results[0].alternatives[0].transcript
                        logger.info(f"  English transcript: '{transcript_english}'")
                        best_transcript = transcript_english
                        best_lang = self.primary_language.upper()
                
                if not best_transcript:
                    logger.warning("Empty transcript from all attempts")
                    return ("", self.primary_language)
                
                # Validate language code
                if best_lang not in VALID_LANGS:
                    logger.warning(f"Invalid language code '{best_lang}', defaulting to {self.primary_language}")
                    best_lang = self.primary_language.upper()
                
                self.detected_language = best_lang
                logger.info(f"FINAL - Language: {best_lang}, Text: '{best_transcript[:100]}'")
                
                return (best_transcript, best_lang)
                
            except Exception as e:
                logger.error(f"Google STT recognition failed: {e}")
                return ("", self.primary_language)

        # Fallback: Hugging Face pipeline
        transcription = self.model(audio, **self.generation_args)

        return transcription["text"].strip()
