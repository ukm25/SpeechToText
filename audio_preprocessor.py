"""
Audio preprocessing module for Vietnamese Speech-to-Text
Handles audio format conversion, resampling, and normalization
"""
import librosa
import soundfile as sf
import numpy as np
from pydub import AudioSegment
import io
import os
from typing import Union, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioPreprocessor:
    """Audio preprocessing class for speech-to-text"""
    
    def __init__(self, target_sample_rate: int = 16000):
        self.target_sample_rate = target_sample_rate
        
    def validate_audio_file(self, file_path: str, max_duration: int = 600, max_size_mb: int = 100) -> bool:
        """
        Validate audio file constraints
        
        Args:
            file_path: Path to audio file
            max_duration: Maximum duration in seconds
            max_size_mb: Maximum file size in MB
            
        Returns:
            bool: True if file is valid, False otherwise
        """
        try:
            # Check file size
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if file_size_mb > max_size_mb:
                logger.error(f"File size {file_size_mb:.2f}MB exceeds limit of {max_size_mb}MB")
                return False
            
            # Check duration
            try:
                duration = librosa.get_duration(path=file_path)
                if duration > max_duration:
                    logger.error(f"Duration {duration:.2f}s exceeds limit of {max_duration}s")
                    return False
            except Exception as duration_error:
                logger.warning(f"Could not get duration using librosa: {duration_error}")
                # Try alternative method
                try:
                    import soundfile as sf
                    info = sf.info(file_path)
                    duration = info.duration
                    if duration > max_duration:
                        logger.error(f"Duration {duration:.2f}s exceeds limit of {max_duration}s")
                        return False
                except Exception as sf_error:
                    logger.warning(f"Could not get duration using soundfile: {sf_error}")
                    # Skip duration check if both methods fail
                    pass
                
            return True
            
        except Exception as e:
            logger.error(f"Error validating audio file: {e}")
            return False
    
    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """
        Load audio file and return audio array and sample rate
        Supports both audio and video files
        
        Args:
            file_path: Path to audio/video file
            
        Returns:
            Tuple of (audio_array, sample_rate)
        """
        try:
            # Try loading with librosa first
            try:
                audio, sr = librosa.load(file_path, sr=None, mono=False)
                logger.info(f"Loaded audio with librosa: {audio.shape}, sample_rate: {sr}")
            except Exception as librosa_error:
                logger.warning(f"Librosa failed: {librosa_error}")
                # Try with soundfile as fallback
                try:
                    import soundfile as sf
                    audio, sr = sf.read(file_path)
                    if len(audio.shape) > 1:
                        audio = librosa.to_mono(audio)
                    logger.info(f"Loaded audio with soundfile: {audio.shape}, sample_rate: {sr}")
                except Exception as sf_error:
                    logger.error(f"Both librosa and soundfile failed: {sf_error}")
                    raise Exception(f"Could not load audio file. Librosa error: {librosa_error}, Soundfile error: {sf_error}")
            
            # Convert to mono if stereo
            if len(audio.shape) > 1:
                audio = librosa.to_mono(audio)
                
            logger.info(f"Final audio: {audio.shape}, sample_rate: {sr}")
            return audio, sr
            
        except Exception as e:
            logger.error(f"Error loading audio: {e}")
            raise
    
    def resample_audio(self, audio: np.ndarray, original_sr: int, target_sr: int = None) -> np.ndarray:
        """
        Resample audio to target sample rate
        
        Args:
            audio: Audio array
            original_sr: Original sample rate
            target_sr: Target sample rate (default: self.target_sample_rate)
            
        Returns:
            Resampled audio array
        """
        if target_sr is None:
            target_sr = self.target_sample_rate
            
        if original_sr == target_sr:
            return audio
            
        try:
            resampled_audio = librosa.resample(audio, orig_sr=original_sr, target_sr=target_sr)
            logger.info(f"Resampled audio from {original_sr}Hz to {target_sr}Hz")
            return resampled_audio
            
        except Exception as e:
            logger.error(f"Error resampling audio: {e}")
            raise
    
    def normalize_audio(self, audio: np.ndarray, target_db: float = -20.0) -> np.ndarray:
        """
        Normalize audio volume to target dB level
        
        Args:
            audio: Audio array
            target_db: Target dB level for normalization
            
        Returns:
            Normalized audio array
        """
        try:
            # Calculate current RMS
            rms = np.sqrt(np.mean(audio**2))
            if rms == 0:
                return audio
                
            # Calculate target RMS
            target_rms = 10**(target_db / 20)
            
            # Normalize
            normalized_audio = audio * (target_rms / rms)
            
            # Clip to prevent distortion
            normalized_audio = np.clip(normalized_audio, -1.0, 1.0)
            
            logger.info(f"Normalized audio to {target_db}dB")
            return normalized_audio
            
        except Exception as e:
            logger.error(f"Error normalizing audio: {e}")
            raise
    
    def preprocess_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """
        Complete audio preprocessing pipeline
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Tuple of (processed_audio, sample_rate)
        """
        try:
            # Validate file (with more lenient validation)
            if not self.validate_audio_file(file_path):
                logger.warning("Audio file validation failed, but attempting to process anyway...")
            
            # Load audio
            audio, original_sr = self.load_audio(file_path)
            
            # Resample to target sample rate
            audio = self.resample_audio(audio, original_sr)
            
            # Normalize audio
            audio = self.normalize_audio(audio)
            
            logger.info(f"Audio preprocessing completed: shape={audio.shape}, sr={self.target_sample_rate}")
            return audio, self.target_sample_rate
            
        except Exception as e:
            logger.error(f"Error in audio preprocessing: {e}")
            raise
    
    def preprocess_audio_from_array(self, audio: np.ndarray, sample_rate: int) -> Tuple[np.ndarray, int]:
        """
        Preprocess audio from numpy array (for YouTube streaming)
        
        Args:
            audio: Audio array
            sample_rate: Sample rate of audio
            
        Returns:
            Tuple of (processed_audio, sample_rate)
        """
        try:
            # Resample to target sample rate
            audio = self.resample_audio(audio, sample_rate)
            
            # Normalize audio
            audio = self.normalize_audio(audio)
            
            logger.info(f"Audio preprocessing from array completed: shape={audio.shape}, sr={self.target_sample_rate}")
            return audio, self.target_sample_rate
            
        except Exception as e:
            logger.error(f"Error in audio preprocessing from array: {e}")
            raise
    
    def save_processed_audio(self, audio: np.ndarray, sample_rate: int, output_path: str) -> None:
        """
        Save processed audio to file
        
        Args:
            audio: Audio array
            sample_rate: Sample rate
            output_path: Output file path
        """
        try:
            sf.write(output_path, audio, sample_rate)
            logger.info(f"Saved processed audio to {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving audio: {e}")
            raise
