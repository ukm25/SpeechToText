"""
Vietnamese Speech-to-Text - Minimal Version
Simple video upload and transcription with Whisper
"""
import streamlit as st
import os
import tempfile
import logging
import numpy as np
from typing import Tuple

# Import our modules
from audio_preprocessor import AudioPreprocessor
from speech_model import VietnameseSpeechModel
from text_postprocessor import TextPostprocessor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Vietnamese Speech-to-Text",
    page_icon="🎤",
    layout="centered"
)

# Initialize components
@st.cache_resource
def get_components():
    return (
        AudioPreprocessor(),
        VietnameseSpeechModel(model_type="whisper"),
        TextPostprocessor()
    )

def transcribe_long_audio(speech_model, audio: np.ndarray, sample_rate: int) -> str:
    """Transcribe long audio by chunking"""
    chunk_samples = 30 * sample_rate  # 30 seconds
    total_chunks = len(audio) // chunk_samples + (1 if len(audio) % chunk_samples > 0 else 0)
    
    transcriptions = []
    for i in range(total_chunks):
        start_idx = i * chunk_samples
        end_idx = min((i + 1) * chunk_samples, len(audio))
        chunk = audio[start_idx:end_idx]
        
        if len(chunk) > 0:
            chunk_transcription = speech_model.transcribe(chunk, sample_rate)
            if chunk_transcription.strip():
                transcriptions.append(chunk_transcription.strip())
    
    return " ".join(transcriptions)

def transcribe_video(video_file_path: str) -> Tuple[str, str]:
    """Transcribe video file"""
    try:
        if not os.path.exists(video_file_path):
            return "", "❌ Video file not found!"
        
        audio_preprocessor, speech_model, text_postprocessor = get_components()
        
        # Extract and preprocess audio
        with st.spinner("🔄 Processing video..."):
            audio, sample_rate = audio_preprocessor.preprocess_audio(video_file_path)
        
        # Transcribe
        with st.spinner("🎯 Transcribing..."):
            if len(audio) > 30 * sample_rate:
                raw_transcription = transcribe_long_audio(speech_model, audio, sample_rate)
            else:
                raw_transcription = speech_model.transcribe(audio, sample_rate)
        
        # Postprocess
        with st.spinner("📝 Finalizing..."):
            processed_text = text_postprocessor.postprocess(
                raw_transcription,
                add_punctuation=True,
                capitalize=True
            )
        
        return processed_text, "✅ Transcription completed!"
        
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return "", f"❌ Error: {str(e)}"

def main():
    """Main app"""
    
    # Header
    st.title("🎤 Vietnamese Speech-to-Text")
    st.caption("Upload a video file to convert speech to text")
    
    # File upload
    video_file = st.file_uploader(
        "Choose a video file",
        type=['mp4', 'avi', 'mov', 'mkv', 'webm'],
        help="Max 10 minutes, 100MB"
    )
    
    # Transcribe button
    if st.button("🎯 Transcribe Video", type="primary", disabled=video_file is None):
        if video_file is not None:
            # Save uploaded video temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(video_file.name)[1]) as temp_file:
                temp_file.write(video_file.read())
                temp_file_path = temp_file.name
            
            try:
                # Transcribe
                result, status = transcribe_video(temp_file_path)
                
                # Store results
                st.session_state['transcription_result'] = result
                st.session_state['transcription_status'] = status
                
            finally:
                # Clean up
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
    
    # Status
    if 'transcription_status' in st.session_state:
        st.success(st.session_state['transcription_status'])
    
    # Result
    if 'transcription_result' in st.session_state and st.session_state['transcription_result']:
        st.subheader("📝 Transcription Result")
        
        # Text area
        st.text_area(
            "Transcribed Text",
            value=st.session_state['transcription_result'],
            height=300,
            label_visibility="collapsed"
        )
        
        # Download
        st.download_button(
            "💾 Download as TXT",
            data=st.session_state['transcription_result'],
            file_name="transcription.txt",
            mime="text/plain"
        )
    
    # Footer
    st.markdown("---")
    st.caption("Powered by OpenAI Whisper")

if __name__ == "__main__":
    main()
