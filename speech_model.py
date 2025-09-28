"""
Speech-to-Text model module for Vietnamese
Supports both wav2vec2 and Whisper models
"""
import torch
import torchaudio
from transformers import (
    Wav2Vec2ForCTC, 
    Wav2Vec2Processor,
    WhisperForConditionalGeneration,
    WhisperProcessor
)
import numpy as np
import logging
from typing import Union, Optional
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VietnameseSpeechModel:
    """Vietnamese Speech-to-Text model wrapper"""
    
    def __init__(self, model_type: str = "wav2vec2", device: str = "auto"):
        self.model_type = model_type
        self.device = self._get_device(device)
        self.model = None
        self.processor = None
        self._load_model()
        
    def _get_device(self, device: str) -> str:
        """Determine the best device to use"""
        if device == "auto":
            if torch.cuda.is_available():
                return "cuda"
            elif torch.backends.mps.is_available():
                return "mps"
            else:
                return "cpu"
        return device
    
    def _load_model(self):
        """Load the specified model and processor"""
        try:
            if self.model_type == "wav2vec2":
                self._load_wav2vec2_model()
            elif self.model_type == "whisper":
                self._load_whisper_model()
            else:
                raise ValueError(f"Unsupported model type: {self.model_type}")
                
            logger.info(f"Loaded {self.model_type} model on {self.device}")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def _load_wav2vec2_model(self):
        """Load wav2vec2 model for Vietnamese"""
        model_name = "facebook/wav2vec2-base-960h"
        
        try:
            # Load processor
            self.processor = Wav2Vec2Processor.from_pretrained(
                model_name
            )
            
            # Load model
            self.model = Wav2Vec2ForCTC.from_pretrained(
                model_name
            )
            
            # Move to device (fallback to CPU if MPS fails)
            try:
                self.model.to(self.device)
            except Exception as device_error:
                logger.warning(f"Failed to move wav2vec2 to {self.device}, using CPU: {device_error}")
                self.device = "cpu"
                self.model.to(self.device)
            
            self.model.eval()
            
        except Exception as e:
            logger.error(f"Error loading wav2vec2 model: {e}")
            raise
        
    def _load_whisper_model(self):
        """Load Whisper model"""
        model_name = "openai/whisper-small"
        
        # Load processor
        self.processor = WhisperProcessor.from_pretrained(
            model_name
        )
        
        # Load model
        self.model = WhisperForConditionalGeneration.from_pretrained(
            model_name
        )
        
        # Move to device
        self.model.to(self.device)
        self.model.eval()
    
    def transcribe_wav2vec2(self, audio: np.ndarray, sample_rate: int) -> str:
        """
        Transcribe audio using wav2vec2 model
        
        Args:
            audio: Audio array
            sample_rate: Sample rate of audio
            
        Returns:
            Transcribed text
        """
        try:
            # Process audio
            inputs = self.processor(
                audio, 
                sampling_rate=sample_rate, 
                return_tensors="pt", 
                padding=True
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Inference
            with torch.no_grad():
                logits = self.model(**inputs).logits
            
            # Decode
            predicted_ids = torch.argmax(logits, dim=-1)
            transcription = self.processor.batch_decode(predicted_ids)[0]
            
            return transcription
            
        except Exception as e:
            logger.error(f"Error in wav2vec2 transcription: {e}")
            raise
    
    def transcribe_whisper(self, audio: np.ndarray, sample_rate: int) -> str:
        """
        Transcribe audio using Whisper model
        
        Args:
            audio: Audio array
            sample_rate: Sample rate of audio
            
        Returns:
            Transcribed text
        """
        try:
            # Process audio
            inputs = self.processor(
                audio, 
                sampling_rate=sample_rate, 
                return_tensors="pt"
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate transcription
            with torch.no_grad():
                generated_ids = self.model.generate(
                    inputs["input_features"],
                    max_length=448,
                    num_beams=5,
                    early_stopping=True
                )
            
            # Decode
            transcription = self.processor.batch_decode(
                generated_ids, 
                skip_special_tokens=True
            )[0]
            
            return transcription
            
        except Exception as e:
            logger.error(f"Error in Whisper transcription: {e}")
            raise
    
    def transcribe(self, audio: np.ndarray, sample_rate: int) -> str:
        """
        Transcribe audio using the loaded model
        
        Args:
            audio: Audio array
            sample_rate: Sample rate of audio
            
        Returns:
            Transcribed text
        """
        try:
            print(f"🎯 SPEECH MODEL TRANSCRIBE:")
            print(f"📊 Audio shape: {audio.shape}")
            print(f"🔊 Sample rate: {sample_rate}")
            print(f"🤖 Model type: {self.model_type}")
            print(f"💻 Device: {self.device}")
            
            if self.model_type == "wav2vec2":
                result = self.transcribe_wav2vec2(audio, sample_rate)
            elif self.model_type == "whisper":
                result = self.transcribe_whisper(audio, sample_rate)
            else:
                raise ValueError(f"Unsupported model type: {self.model_type}")
            
            print(f"📝 Transcription result: \"{result}\"")
            return result
                
        except Exception as e:
            logger.error(f"Error in transcription: {e}")
            print(f"❌ Transcription error: {e}")
            raise
    
    def get_model_info(self) -> dict:
        """Get model information"""
        return {
            "model_type": self.model_type,
            "device": self.device,
            "model_name": self.model.config.name_or_path if hasattr(self.model.config, 'name_or_path') else "unknown"
        }
