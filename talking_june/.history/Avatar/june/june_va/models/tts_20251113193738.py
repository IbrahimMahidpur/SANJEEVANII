"""
This module provides a Text-to-Speech (TTS) class for generating speech from text using the TTS library or Google Cloud Text-to-Speech.
"""

from typing import List, Union
import os

from .common import BaseModel


class TTS(BaseModel):
    """
    A class for generating speech from text using the TTS library.

    This class inherits from the BaseModel class and provides a method for running
    the Text-to-Speech model on text input.

    Args:
        **kwargs: Keyword arguments for initializing the TTS model, including optional
            arguments like 'device', 'generation_args', and 'model'.

    Attributes:
        model: An instance of the TTS model from the TTS library.
        file_path: The file path where the generated audio should be saved.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        # Disable additional splits, as they increase the likelihood of generation errors.
        self.generation_args["split_sentences"] = False

        self.file_path: str = self.generation_args.get("file_path") or "out.wav"

        # Support Google Cloud Text-to-Speech when `model` is set to "google"
        if str(self.model_id).lower() in ("google", "gcloud", "google-tts"):
            try:
                from google.oauth2 import service_account
                from google.cloud import texttospeech
            except Exception:
                raise RuntimeError("Google Cloud Text-to-Speech package not installed. Install 'google-cloud-texttospeech'.")

            cred_path = self.generation_args.get("credentials")
            creds = None
            if cred_path:
                creds = service_account.Credentials.from_service_account_file(cred_path)

            self._gc_client = texttospeech.TextToSpeechClient(credentials=creds)
            self._gc_tts = texttospeech
            
            # Multilingual config
            self.language_code = self.generation_args.get("language_code", "en-US")
            self.voice_name = self.generation_args.get("voice_name", None)  # e.g., "en-IN-Wavenet-C"
            self.ssml_gender = self.generation_args.get("ssml_gender", "NEUTRAL")
            self.sample_rate_hertz = int(self.generation_args.get("sample_rate_hertz", 24000))
            self.speaking_rate = float(self.generation_args.get("speaking_rate", 1.0))
            self.pitch = float(self.generation_args.get("pitch", 0.0))
            self.audio_encoding = texttospeech.AudioEncoding.LINEAR16
            
            # Track generated files for cleanup
            self._generated_files = []
            # default output path
            self.file_path = self.generation_args.get("file_path") or self.file_path
            return

        from TTS.api import TTS as CoquiTTS

        self.model = CoquiTTS(self.model_id).to(self.device)

    def _get_voice_for_language(self, language_code: str) -> str:
        """
        Get appropriate voice name for a language code.
        Uses high-quality Neural2 and Wavenet voices for best pronunciation.
        
        Args:
            language_code: Language code like "hi-IN", "en-US", "bn-IN"
            
        Returns:
            Voice name suitable for that language
        """
        # Normalize language code to uppercase
        language_code = language_code.upper() if language_code else ""
        
        # Auto-select highest-quality voices for each language
        # Neural2 > Wavenet > Standard (in order of quality)
        voice_map = {
            "HI-IN": "hi-IN-Neural2-A",    # Hindi female (best quality)
            "HI": "hi-IN-Neural2-A",        # Fallback for just "hi"
            "EN-IN": "en-IN-Neural2-D",     # Indian English female
            "EN-US": "en-US-Neural2-F",     # US English female
            "EN": "en-IN-Neural2-D",        # Default English to Indian
            "BN-IN": "bn-IN-Wavenet-A",     # Bengali female
            "BN": "bn-IN-Wavenet-A",        # Fallback for just "bn"
            "TA-IN": "ta-IN-Wavenet-A",     # Tamil female
            "TE-IN": "te-IN-Standard-A",    # Telugu female
            "MR-IN": "mr-IN-Wavenet-A",     # Marathi female
            "GU-IN": "gu-IN-Wavenet-A",     # Gujarati female
        }
        
        # Try exact match first, then without country code
        selected_voice = voice_map.get(language_code)
        if not selected_voice and '-' in language_code:
            # Try just the language part (e.g., "HI-IN" -> "HI")
            lang_only = language_code.split('-')[0]
            selected_voice = voice_map.get(lang_only)
        
        return selected_voice

    def forward(self, text: str, ssml: bool = False, language_code: str = None) -> Union[List[int], str]:
        """
        Generate speech from text using the Text-to-Speech model.

        Args:
            text: The input text for which speech should be generated.
            ssml: If True, treat text as SSML markup (Google TTS only).
            language_code: Override language code for this synthesis (e.g., "hi-IN", "en-US").

        Returns:
            A list of integers representing the generated audio data (Coqui),
            or a string path to the generated WAV file (Google TTS).
        """

        # Google Cloud TTS path: synthesize and save to file, return path string
        if hasattr(self, "_gc_client"):
            # Prepare input
            if ssml:
                synthesis_input = self._gc_tts.SynthesisInput(ssml=text)
            else:
                synthesis_input = self._gc_tts.SynthesisInput(text=text)

            # Use provided language_code or default
            target_lang = language_code or self.language_code
            
            # Auto-select voice based on language for better pronunciation
            voice_name = self._get_voice_for_language(target_lang)
            
            # Log voice selection for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"🎤 TTS Voice Selection: lang={target_lang}, voice={voice_name}")
            
            # voice selection with proper language-specific voice
            voice_params = {
                "language_code": target_lang,
                "ssml_gender": getattr(
                    self._gc_tts.SsmlVoiceGender,
                    self.ssml_gender.upper(),
                    self._gc_tts.SsmlVoiceGender.NEUTRAL
                ),
            }
            
            # Use language-specific voice for better pronunciation
            if voice_name:
                voice_params["name"] = voice_name
            else:
                # Fallback to configured voice only if no language-specific voice found
                voice_params["name"] = self.voice_name
                
            voice = self._gc_tts.VoiceSelectionParams(**voice_params)

            # Adjust speaking rate for Hindi/Hinglish for clearer pronunciation
            adjusted_speaking_rate = self.speaking_rate
            if target_lang.upper().startswith('HI'):
                # Slightly slower for Hindi for better clarity
                adjusted_speaking_rate = max(0.85, self.speaking_rate - 0.15)
            
            audio_config = self._gc_tts.AudioConfig(
                audio_encoding=self.audio_encoding,
                sample_rate_hertz=self.sample_rate_hertz,
                speaking_rate=adjusted_speaking_rate,
                pitch=self.pitch,
            )

            # Attempt synthesis; some Google voices / genders may be unsupported
            # in certain regions. If we get an InvalidArgument mentioning
            # neutral/gender, retry with a supported gender (FEMALE) as a fallback.
            try:
                response = self._gc_client.synthesize_speech(
                    input=synthesis_input, voice=voice, audio_config=audio_config
                )
            except Exception as e:
                msg = str(e)
                if "neutral" in msg.lower() or "gender neutral" in msg.lower():
                    # Log and retry with FEMALE
                    try:
                        fallback_gender = self._gc_tts.SsmlVoiceGender.FEMALE
                        voice_params["ssml_gender"] = fallback_gender
                        voice = self._gc_tts.VoiceSelectionParams(**voice_params)
                        response = self._gc_client.synthesize_speech(
                            input=synthesis_input, voice=voice, audio_config=audio_config
                        )
                    except Exception:
                        # Re-raise the original exception if retry fails
                        raise
                else:
                    # Not a gender-related error; re-raise
                    raise

            # Write to WAV file using wave module (response.audio_content is raw PCM for LINEAR16)
            import wave
            import tempfile

            # Use a unique temporary file per synthesis to avoid file lock conflicts on Windows
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            out_path = tmp.name
            tmp.close()

            with wave.open(out_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16 bits
                wf.setframerate(audio_config.sample_rate_hertz)
                wf.writeframes(response.audio_content)

            # Track generated files so caller can clean them up
            if not hasattr(self, "_generated_files"):
                self._generated_files = []
            self._generated_files.append(out_path)

            return out_path

        # Default: Coqui TTS returns waveform/list that existing consumer expects
        return self.model.tts(text, **self.generation_args)
