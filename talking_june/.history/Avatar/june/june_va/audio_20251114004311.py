"""
This module provides classes and functions for recording and playing audio.
"""

import logging
import time
from typing import Dict, List, Optional, Union

import numpy as np
import pygame.mixer

from .utils import print_system_message, suppress_stdout_stderr


class AudioIO:
    """Simple audio I/O helper used by the CLI for recording and optional playback.

    Methods are small and synchronous to match the original design. The
    recorder will observe both an instance-level pause flag and a module-
    level `capture_paused_global` flag so other processes (e.g. the bridge
    listener) can globally pause capture.
    """

    RATE = 24000
    CHUNK = 2048
    THRESHOLD = 500  # Lowered from 800 for better voice detection
    SILENCE_LIMIT = 3

    def __enter__(self) -> "AudioIO":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def __init__(self) -> None:
        self.pa = None
        self.input_stream = None
        self.capture_paused = False

    def pause_capture(self) -> None:
        self.capture_paused = True

    def resume_capture(self) -> None:
        self.capture_paused = False

    def _initialize_input_stream(self) -> None:
        import pyaudio

        with suppress_stdout_stderr():
            self.pa = pyaudio.PyAudio()
        
        # Get default input device info for diagnostics
        try:
            default_input = self.pa.get_default_input_device_info()
            logger = logging.getLogger(__name__)
            logger.info(f"🎤 Using microphone: {default_input.get('name', 'Unknown')}")
            logger.info(f"   Max input channels: {default_input.get('maxInputChannels', 0)}")
            logger.info(f"   Default sample rate: {default_input.get('defaultSampleRate', 0)}")
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.warning(f"⚠️  Could not get microphone info: {e}")

        self.input_stream = self.pa.open(
            channels=1,
            format=pyaudio.paInt16,
            frames_per_buffer=self.CHUNK,
            input=True,
            rate=self.RATE,
        )

    def close(self) -> None:
        if self.input_stream:
            try:
                self.input_stream.stop_stream()
            except Exception:
                pass
            try:
                self.input_stream.close()
            except Exception:
                pass
        if self.pa:
            try:
                self.pa.terminate()
            except Exception:
                pass

    @staticmethod
    def is_silent(data: np.ndarray) -> bool:
        try:
            return np.max(np.abs(data)) < AudioIO.THRESHOLD
        except Exception:
            return True

    @staticmethod
    def play_wav(file_path: str) -> None:
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
        except Exception:
            logging.getLogger(__name__).exception("Failed to play wav: %s", file_path)

    def record_audio(self) -> Optional[Dict[str, Union[int, np.ndarray]]]:
        if not self.input_stream:
            self._initialize_input_stream()

        frames: List[np.ndarray] = []
        current_silence = 0
        recording = False

        try:
            self.input_stream.start_stream()
        except Exception:
            # Some backends don't require explicit start
            pass

        print_system_message("Listening for sound...", log_level=logging.INFO)

        # Diagnostic: Show if capture is paused
        paused_check_count = 0
        check_count = 0  # For periodic audio level display
        
        while True:
            # honor pauses
            if getattr(self, "capture_paused", False) or globals().get("capture_paused_global", False):
                paused_check_count += 1
                if paused_check_count == 1:  # Log only once when paused
                    print_system_message("⏸️  Capture is PAUSED (waiting for resume...)", log_level=logging.WARNING)
                time.sleep(0.1)
                continue
            
            # Reset pause counter when not paused
            if paused_check_count > 0:
                print_system_message("▶️  Capture RESUMED", log_level=logging.INFO)
                paused_check_count = 0

            try:
                raw = self.input_stream.read(self.CHUNK)
            except Exception as e:
                # Reading can fail if stream is closed; return None to indicate no audio
                print_system_message(f"⚠️  Audio read failed: {e}", log_level=logging.ERROR)
                return None

            data: np.ndarray = np.frombuffer(raw, dtype=np.int16)
            
            # Diagnostic: Show audio level periodically (every 20 chunks = ~1.7 seconds)
            if not recording:
                check_count += 1
                if check_count % 20 == 0:
                    audio_level = int(np.max(np.abs(data)))
                    if audio_level > 50:  # Only show if there's some audio
                        print_system_message(f"🎤 Audio level: {audio_level} (threshold: {self.THRESHOLD})", log_level=logging.DEBUG)

            if not recording and not self.is_silent(data):
                print_system_message("Sound detected, starting recording...", log_level=logging.INFO)
                print_system_message("Sound detected, starting recording...", log_level=logging.INFO)
                print_system_message("Sound detected, starting recording...", log_level=logging.INFO)
                recording = True

            if recording:
                frames.append(data)
                if self.is_silent(data):
                    current_silence += 1
                else:
                    current_silence = 0

                if current_silence > (self.SILENCE_LIMIT * self.RATE / self.CHUNK):
                    print_system_message("Silence detected, stopping recording...", log_level=logging.INFO)
                    break

        try:
            self.input_stream.stop_stream()
        except Exception:
            pass

        if recording and frames:
            raw_data = np.hstack(frames)
            normalized_data = raw_data.astype(np.float32) / np.iinfo(np.int16).max
            return {"raw": normalized_data, "sampling_rate": self.RATE}

        return None


# Module-level pause flag and helpers. Some parts of the codebase may not hold
# a reference to the current AudioIO instance, so these provide a global
# control point that `record_audio` will also observe.
capture_paused_global = False

def pause_capture_global() -> None:
    global capture_paused_global
    capture_paused_global = True

def resume_capture_global() -> None:
    global capture_paused_global
    capture_paused_global = False
