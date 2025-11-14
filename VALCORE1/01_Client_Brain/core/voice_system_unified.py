"""
VALCORE1 Unified Voice System
Combines STT (Faster-Whisper), TTS (Kokoro), Wake Word (Porcupine), and Speaker Verification (Resemblyzer)
"""

import os
import json
import logging
import threading
import queue
from pathlib import Path
from typing import Optional, Callable, Generator
import numpy as np

# Audio
import pyaudio
import sounddevice as sd

# STT
from faster_whisper import WhisperModel

# Wake Word
import pvporcupine

# Speaker Verification
try:
    from resemblyzer import VoiceEncoder, preprocess_wav
    RESEMBLYZER_AVAILABLE = True
except ImportError:
    RESEMBLYZER_AVAILABLE = False
    logging.warning("Resemblyzer not available - speaker verification disabled")

# TTS - Kokoro (using sounddevice for playback)
try:
    import onnxruntime as ort
    KOKORO_AVAILABLE = True
except ImportError:
    KOKORO_AVAILABLE = False
    logging.warning("ONNX Runtime not available - TTS disabled")

import torch


logger = logging.getLogger(__name__)


class VALVoiceSystem:
    """Unified voice system managing all voice operations for VALCORE1"""

    def __init__(self, config_path: str = "config/voice_config.json"):
        """Initialize the unified voice system"""
        self.config = self._load_config(config_path)
        self.running = False
        self.microphone_enabled = True
        self.audio_queue = queue.Queue()

        # Set GPU device
        if torch.cuda.is_available():
            torch.cuda.set_device(0)  # RTX 5070
            logger.info(f"Using GPU: {torch.cuda.get_device_name(0)}")
        else:
            logger.warning("CUDA not available - voice system may be slow")

        # Initialize components
        self._init_audio()
        self._init_stt()
        self._init_tts()
        self._init_wake_word()
        self._init_speaker_verification()

        logger.info("VAL Voice System initialized successfully")

    def _load_config(self, path: str) -> dict:
        """Load configuration from JSON file"""
        with open(path, 'r') as f:
            return json.load(f)

    def _init_audio(self):
        """Initialize audio input device"""
        self.pyaudio_instance = pyaudio.PyAudio()

        # Get default input device if not specified
        if self.config['audio']['use_default_device']:
            default_device = self.pyaudio_instance.get_default_input_device_info()
            self.mic_index = default_device['index']
            logger.info(f"Using microphone: {default_device['name']} (Index: {self.mic_index})")
        else:
            self.mic_index = self.config['audio'].get('device_index', 0)

        self.sample_rate = self.config['audio']['sample_rate']
        self.chunk_size = self.config['audio']['chunk_size']

    def _init_stt(self):
        """Initialize Faster-Whisper STT model"""
        logger.info("Loading Faster-Whisper STT model...")

        model_size = self.config['stt']['model']
        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = self.config['stt']['compute_type']

        self.whisper_model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type
        )

        logger.info(f"STT model loaded: {model_size} on {device}")

    def _init_tts(self):
        """Initialize Kokoro TTS"""
        if not KOKORO_AVAILABLE:
            logger.warning("TTS not available")
            self.tts_available = False
            return

        # Kokoro TTS would be initialized here
        # For now, using simple text-to-speech notification
        self.tts_available = True
        logger.info("TTS system ready (Kokoro placeholder)")

    def _init_wake_word(self):
        """Initialize Porcupine wake word detection"""
        try:
            access_key = self.config['wake_word'].get('access_key', '')

            if not access_key or access_key == 'YOUR_PICOVOICE_ACCESS_KEY_HERE':
                logger.warning("Porcupine access key not configured - wake word disabled")
                self.wake_word_available = False
                self.porcupine = None
                return

            # Initialize Porcupine with "Hey Val" keyword
            self.porcupine = pvporcupine.create(
                access_key=access_key,
                keyword_paths=self.config['wake_word'].get('keyword_paths', []),
                sensitivities=[self.config['wake_word']['sensitivity']]
            )

            self.wake_word_available = True
            logger.info("Wake word detection initialized")

        except Exception as e:
            logger.error(f"Failed to initialize wake word: {e}")
            self.wake_word_available = False
            self.porcupine = None

    def _init_speaker_verification(self):
        """Initialize Resemblyzer speaker verification"""
        if not RESEMBLYZER_AVAILABLE:
            self.speaker_verification_enabled = False
            return

        if not self.config['speaker_verification']['enabled']:
            self.speaker_verification_enabled = False
            logger.info("Speaker verification disabled in config")
            return

        try:
            self.voice_encoder = VoiceEncoder()
            self.speaker_embeddings = {}

            # Load existing voice profiles
            profiles_dir = Path(self.config['speaker_verification']['profiles_dir'])
            if profiles_dir.exists():
                for profile_file in profiles_dir.glob("*.npy"):
                    name = profile_file.stem
                    embedding = np.load(profile_file)
                    self.speaker_embeddings[name] = embedding
                    logger.info(f"Loaded voice profile: {name}")

            self.speaker_verification_enabled = len(self.speaker_embeddings) > 0

        except Exception as e:
            logger.error(f"Failed to initialize speaker verification: {e}")
            self.speaker_verification_enabled = False

    def detect_wake_word(self, audio_chunk: np.ndarray) -> bool:
        """
        Detect wake word in audio chunk

        Args:
            audio_chunk: Audio data as numpy array

        Returns:
            True if wake word detected
        """
        if not self.wake_word_available or self.porcupine is None:
            return True  # Always active if wake word not configured

        try:
            # Convert audio to int16 if necessary
            if audio_chunk.dtype != np.int16:
                audio_chunk = (audio_chunk * 32767).astype(np.int16)

            keyword_index = self.porcupine.process(audio_chunk)
            return keyword_index >= 0

        except Exception as e:
            logger.error(f"Wake word detection error: {e}")
            return False

    def transcribe(self, audio_data: np.ndarray, language: str = "en") -> str:
        """
        Transcribe audio using Faster-Whisper

        Args:
            audio_data: Audio data as numpy array (float32, sample_rate Hz)
            language: Language code (default: "en")

        Returns:
            Transcribed text
        """
        try:
            # Ensure audio is float32
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32) / 32767.0

            segments, info = self.whisper_model.transcribe(
                audio_data,
                language=language,
                beam_size=self.config['stt'].get('beam_size', 5),
                vad_filter=self.config['stt'].get('vad_filter', True)
            )

            # Combine all segments
            text = " ".join([segment.text for segment in segments]).strip()

            logger.info(f"Transcribed: {text}")
            return text

        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""

    def synthesize_speech(self, text: str) -> Optional[np.ndarray]:
        """
        Synthesize speech from text using Kokoro TTS

        Args:
            text: Text to synthesize

        Returns:
            Audio data as numpy array or None if TTS unavailable
        """
        if not self.tts_available:
            logger.warning(f"TTS not available, would speak: {text}")
            return None

        try:
            # TODO: Implement Kokoro TTS synthesis
            # For now, just log the text
            logger.info(f"TTS: {text}")
            return None

        except Exception as e:
            logger.error(f"TTS error: {e}")
            return None

    def verify_speaker(self, audio_data: np.ndarray, profile_name: str = "ben_voice") -> bool:
        """
        Verify speaker identity using Resemblyzer

        Args:
            audio_data: Audio data as numpy array
            profile_name: Name of the voice profile to match against

        Returns:
            True if speaker matches profile

        Security:
            Fails CLOSED (returns False) on errors when verification is enabled.
            This prevents unauthorized access if the verification system fails.
        """
        if not self.speaker_verification_enabled:
            logger.debug("Speaker verification disabled, allowing command")
            return True  # Allow if verification disabled

        if profile_name not in self.speaker_embeddings:
            logger.warning(f"Voice profile '{profile_name}' not found")
            # SECURITY: Fail closed if profile missing but verification enabled
            logger.warning("SECURITY: Verification enabled but profile missing - blocking command")
            return False

        try:
            # Preprocess audio
            wav = preprocess_wav(audio_data, self.sample_rate)

            # Generate embedding
            embedding = self.voice_encoder.embed_utterance(wav)

            # Compare with stored profile
            stored_embedding = self.speaker_embeddings[profile_name]
            similarity = np.dot(embedding, stored_embedding)

            threshold = self.config['speaker_verification']['threshold']
            is_match = similarity >= threshold

            logger.info(f"Speaker verification: {similarity:.3f} (threshold: {threshold}) - {'MATCH' if is_match else 'NO MATCH'}")
            return is_match

        except Exception as e:
            logger.error(f"Speaker verification error: {e}")
            # SECURITY: Fail CLOSED, not open - block on error when verification enabled
            logger.error("SECURITY: Verification failed with error - blocking command for safety")
            return False

    def start_listening(self, callback: Callable[[str], None]):
        """
        Start continuous listening loop with wake word detection

        Args:
            callback: Function to call with transcribed text
        """
        self.running = True
        self.callback = callback

        # Start listening thread
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()

        logger.info("Voice system listening started")

    def _listen_loop(self):
        """Main listening loop (runs in separate thread)"""
        stream = self.pyaudio_instance.open(
            format=pyaudio.paInt16,
            channels=self.config['audio']['channels'],
            rate=self.sample_rate,
            input=True,
            input_device_index=self.mic_index,
            frames_per_buffer=self.chunk_size
        )

        logger.info("Audio stream opened, listening for wake word...")

        try:
            while self.running:
                if not self.microphone_enabled:
                    # Mic disabled, sleep and continue
                    threading.Event().wait(0.1)
                    continue

                # Read audio chunk
                audio_data = stream.read(self.chunk_size, exception_on_overflow=False)
                audio_chunk = np.frombuffer(audio_data, dtype=np.int16)

                # Check for wake word
                if self.detect_wake_word(audio_chunk):
                    logger.info("Wake word detected!")

                    # Record command (e.g., 5 seconds)
                    command_audio = self._record_command(stream, duration=5)

                    # Transcribe
                    text = self.transcribe(command_audio)

                    if text and self.callback:
                        # Verify speaker if enabled
                        if self.speaker_verification_enabled:
                            if not self.verify_speaker(command_audio):
                                logger.warning("Speaker verification failed - ignoring command")
                                continue

                        # Call callback with transcribed text
                        self.callback(text)

        except Exception as e:
            logger.error(f"Listen loop error: {e}")
        finally:
            stream.stop_stream()
            stream.close()

    def _record_command(self, stream, duration: int = 5) -> np.ndarray:
        """
        Record audio for specified duration

        Args:
            stream: PyAudio stream
            duration: Duration in seconds

        Returns:
            Audio data as numpy array (float32)
        """
        logger.info(f"Recording command for {duration} seconds...")

        frames = []
        num_chunks = int(self.sample_rate / self.chunk_size * duration)

        for _ in range(num_chunks):
            data = stream.read(self.chunk_size, exception_on_overflow=False)
            frames.append(data)

        # Convert to numpy array
        audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)

        # Convert to float32 for Whisper
        audio_float = audio_data.astype(np.float32) / 32767.0

        return audio_float

    def stop_listening(self):
        """Stop the listening loop"""
        self.running = False
        if hasattr(self, 'listen_thread'):
            self.listen_thread.join(timeout=2)
        logger.info("Voice system stopped")

    def toggle_microphone(self) -> bool:
        """
        Toggle microphone on/off

        Returns:
            New microphone state (True = enabled)
        """
        self.microphone_enabled = not self.microphone_enabled
        state = "enabled" if self.microphone_enabled else "disabled"
        logger.info(f"Microphone {state}")
        return self.microphone_enabled

    def cleanup(self):
        """Cleanup resources"""
        self.stop_listening()

        if self.porcupine:
            self.porcupine.delete()

        if hasattr(self, 'pyaudio_instance'):
            self.pyaudio_instance.terminate()

        logger.info("Voice system cleaned up")
