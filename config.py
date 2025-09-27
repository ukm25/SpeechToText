"""
Configuration file for Vietnamese Speech-to-Text project
"""
import os

# Model configurations
MODEL_CONFIGS = {
    "wav2vec2": {
        "model_name": "facebook/wav2vec2-base-960h",
        "processor_name": "facebook/wav2vec2-base-960h"
    },
    "whisper": {
        "model_name": "openai/whisper-small",
        "processor_name": "openai/whisper-small"
    }
}

# Audio processing settings
AUDIO_CONFIG = {
    "target_sample_rate": 16000,
    "max_duration_seconds": 600,  # 10 minutes
    "max_file_size_mb": 100,
    "supported_formats": [".wav", ".mp3", ".flac", ".m4a", ".mp4", ".avi", ".mov", ".mkv", ".webm"]
}

# File paths
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
MODEL_CACHE_DIR = "model_cache"

# Create directories if they don't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MODEL_CACHE_DIR, exist_ok=True)

# API settings
API_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "title": "Vietnamese Speech-to-Text API",
    "description": "API for converting Vietnamese speech to text"
}
