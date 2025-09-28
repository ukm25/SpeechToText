"""
Vietnamese Psychological Counseling App - Optimized Version
Simplified and clean code structure
"""
import streamlit as st
import os
import tempfile
import logging
import requests
import json
import io
import hashlib
import re
import base64
import numpy as np
from typing import Tuple, Optional
import time

# Import our modules
from audio_preprocessor import AudioPreprocessor
from speech_model import VietnameseSpeechModel
from text_postprocessor import TextPostprocessor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="AI Tư vấn Tâm lý",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Optimized CSS - Clean and minimal
CSS_STYLES = """
<style>
    /* Hide Streamlit defaults */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Hide hidden inputs completely */
    .stTextInput > div > div > input[type="text"]:empty {
        display: none !important;
    }
    
    /* Hide all stTextInput containers that are empty */
    .stTextInput:has(input[value=""]) {
        display: none !important;
    }
    
    
    /* Main container - Fixed 700px height */
    .main .block-container,
    .stMainBlockContainer, 
    .block-container,
    [class*="stMainBlockContainer"], 
    [class*="block-container"],
    div[data-testid="stAppViewContainer"] {
        height: 700px !important;
        padding: 10px !important;
        padding-top: 80px !important;
        padding-bottom: 120px !important;
        margin: 0 !important;
        max-width: 100% !important;
        border-radius: 20px;
        border: 2px solid #e0e0e0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        background: #f8f9fa;
    }
    
    /* Allow page scroll for chat messages */
    body, html, .stApp {height: 100vh; overflow-y: auto; margin: 0; padding: 0;}
    .stApp > div, .stApp > div > div {margin: 0 !important; padding: 0 !important;}
    
    /* Chat components */
    .chat-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; padding: 15px 20px; text-align: left; font-size: 18px;
        font-weight: 600; border-radius: 15px 15px 0 0; display: flex;
        align-items: center; justify-content: space-between; gap: 12px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        z-index: 1001 !important;
        margin: 0 !important;
        border-radius: 0 !important;
    }
    
           .chat-container {
               background: #ffffff; 
               min-height: 60px; 
               padding: 15px 20px;
               border-left: 1px solid #e0e0e0; 
               border-right: 1px solid #e0e0e0;
               border-bottom: 1px solid #f0f0f0;
               margin-bottom: 2px;
           }
    
    .input-container {
        flex: 1; display: flex; align-items: center; background: white;
        border-radius: 25px; padding: 12px 20px; gap: 15px;
        border: 2px solid #e0e0e0; transition: all 0.3s ease;
        height: 48px; min-height: 48px;
    }
    
    .input-container:focus-within {border-color: #667eea; box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);}
    .input-container.recording {border-color: #ff4757; background: #fff5f5; animation: pulse 1.5s infinite;}
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 71, 87, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(255, 71, 87, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 71, 87, 0); }
    }
    
    .input-field {flex: 1; border: none; outline: none; font-size: 16px; padding: 8px 0; background: transparent; color: #333;}
    .input-field::placeholder {color: #999; font-style: italic;}
    
    .voice-btn {
        background: none; border: none; color: #667eea; font-size: 24px;
        cursor: pointer; padding: 8px; border-radius: 50%; transition: all 0.3s ease;
    }
    .voice-btn:hover {background: #f0f2f5; transform: scale(1.1);}
    .voice-btn.recording {color: #ff4757; background: #fff5f5; animation: bounce 0.6s infinite;}
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-5px); }
        60% { transform: translateY(-3px); }
    }
    
    .send-btn {
        background: #667eea; color: white; border: none; border-radius: 50%;
        width: 40px; height: 40px; display: flex; align-items: center;
        justify-content: center; cursor: pointer; font-size: 16px;
        transition: all 0.3s ease; opacity: 0.7;
    }
    .send-btn:hover {background: #5a6fd8; transform: scale(1.05); opacity: 1;}
    
    .send-button {
        background: #667eea; color: white; border: none; border-radius: 25px;
        padding: 12px 24px; font-size: 16px; font-weight: 600;
        cursor: pointer; transition: all 0.3s ease; opacity: 0.9;
        min-width: 80px; height: 48px; display: flex; align-items: center; justify-content: center;
    }
    .send-button:hover {background: #5a6fd8; transform: scale(1.05); opacity: 1;}
    
    
    /* File uploader - fixed positioning in footer */
    .stFileUploader {
        position: fixed !important;
        bottom: 15px !important;
        left: 20px !important;
        width: calc(35% - 10px) !important;
        height: 60px !important;
        z-index: 1001 !important;
        background: #ffffff !important;
        border: 2px solid #667eea !important;
        border-radius: 15px !important;
        box-shadow: 0 -4px 20px rgba(102, 126, 234, 0.15) !important;
        padding: 8px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        overflow: hidden !important;
    }
    
    /* Ensure all child elements have white background */
    .stFileUploader > div {
        background: #ffffff !important;
    }
    
    .stFileUploader > div > div {
        background: #ffffff !important;
    }
    
    .stFileUploader button {
        background: #ffffff !important;
    }
    
    /* Target the dropzone specifically */
    [data-testid="stFileUploaderDropzone"] {
        background-color: white !important;
    }
    
    /* Hide file uploader label and help text */
    .stFileUploader label {
        display: none !important;
    }
    
    .stFileUploader .stTooltip {
        display: none !important;
    }
    
    .stFileUploader [data-testid="stTooltip"] {
        display: none !important;
    }
    
    /* Hide file name display after upload */
    .stFileUploader > div > div {
        display: none !important;
    }
    
    .stFileUploader .stMarkdown {
        display: none !important;
    }
    
    .stFileUploader .stText {
        display: none !important;
    }
    
    /* Hide all child elements that might show file info */
    .stFileUploader > div > div:not(:first-child) {
        display: none !important;
    }
    
    .stFileUploader div[data-testid="stMarkdownContainer"] {
        display: none !important;
    }
    
    .stFileUploader div[data-testid="stText"] {
        display: none !important;
    }
    
    
    
    .input-area {
        position: fixed !important;
        bottom: 15px !important;
        right: 20px !important;
        width: calc(60% - 20px) !important;
        height: 60px !important;
        z-index: 1001 !important;
        background: #ffffff !important;
        border: 2px solid #667eea !important;
        border-radius: 15px !important;
        box-shadow: 0 -4px 20px rgba(102, 126, 234, 0.15) !important;
        padding: 8px !important;
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
    }
    
    
    
    /* Message bubbles */
    .message-left, .message-right {
        display: flex; align-items: flex-end; gap: 8px; margin-bottom: 10px;
    }
    .message-right {flex-direction: row-reverse;}
    
    .message-avatar {
        width: 32px; height: 32px; border-radius: 50%; display: flex;
        align-items: center; justify-content: center; color: white;
        font-weight: bold; font-size: 12px; flex-shrink: 0;
    }
    .message-left .message-avatar {background: #667eea;}
    .message-right .message-avatar {background: #42b883;}
    
    .message-bubble {
        max-width: 80%; padding: 8px 12px; border-radius: 18px; word-wrap: break-word;
    }
    .message-left .message-bubble {background: #f0f2f5; color: #1c1e21; border-bottom-left-radius: 4px;}
    .message-right .message-bubble {background: #0084ff; color: white; border-bottom-right-radius: 4px;}
    
    /* Custom styling for Streamlit chat messages */
    .stChatMessage[data-testid="user"] {
        flex-direction: row-reverse !important;
    }
    
    .stChatMessage[data-testid="user"] .stChatMessage__avatar {
        order: 2 !important;
        margin-left: 8px !important;
        margin-right: 0 !important;
    }
    
    .stChatMessage[data-testid="user"] .stChatMessage__content {
        order: 1 !important;
        max-width: 80% !important;
        background: #0084ff !important;
        color: white !important;
        border-radius: 18px !important;
        border-bottom-right-radius: 4px !important;
        padding: 8px 12px !important;
        margin-right: 8px !important;
        margin-left: 0 !important;
    }
    
    .stChatMessage[data-testid="assistant"] .stChatMessage__content {
        max-width: 80% !important;
        background: #f0f2f5 !important;
        color: #1c1e21 !important;
        border-radius: 18px !important;
        border-bottom-left-radius: 4px !important;
        padding: 8px 12px !important;
    }
    
    /* Typing indicator */
    .typing-indicator {display: flex; align-items: flex-end; gap: 8px; margin-bottom: 10px;}
    .typing-bubble {
        background: #f0f2f5; border-radius: 18px; padding: 12px 16px;
        border-bottom-left-radius: 4px; display: flex; align-items: center; gap: 4px;
    }
    .typing-dot {
        width: 6px; height: 6px; background: #65676b; border-radius: 50%;
        animation: typing 1.4s infinite;
    }
    .typing-dot:nth-child(2) {animation-delay: 0.2s;}
    .typing-dot:nth-child(3) {animation-delay: 0.4s;}
    
    @keyframes typing {
        0%, 60%, 100% {transform: translateY(0);}
        30% {transform: translateY(-10px);}
    }
</style>
"""

# Initialize components
@st.cache_resource
def get_components():
    return (
        AudioPreprocessor(),
        VietnameseSpeechModel(model_type="whisper"),
        TextPostprocessor()
    )

def transcribe_audio(audio_file_path: str) -> Tuple[str, str]:
    """Transcribe audio file"""
    try:
        audio_preprocessor, speech_model, text_postprocessor = get_components()
        
        # Preprocess audio - FIXED: preprocess_audio returns (audio, sample_rate)
        audio, sample_rate = audio_preprocessor.preprocess_audio(audio_file_path)
        
        if audio is None or len(audio) == 0:
            return None, "Audio preprocessing failed"
        
        # Transcribe - FIXED: transcribe needs (audio, sample_rate)
        transcription = speech_model.transcribe(audio, sample_rate)
        
        if not transcription or not transcription.strip():
            return None, "Transcription failed"
        
        # Postprocess - FIXED: use correct method name
        final_text = text_postprocessor.postprocess(transcription)
        
        # LOG AUDIO CONTENT (TEXT TRANSCRIPTION)
        print("🎤 AUDIO CONTENT (TEXT TRANSCRIPTION):")
        print(f"📝 Raw audio content: \"{transcription}\"")
        print(f"📝 Processed audio content: \"{final_text}\"")
        print(f"📝 Audio content length: {len(final_text)} characters")
        print(f"📝 Audio content words: {len(final_text.split())} words")
        print("🎤 END AUDIO CONTENT (TEXT TRANSCRIPTION)")
        
        return final_text, "Success"
        
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return None, f"Error: {str(e)}"

def process_audio_safely(audio_data: str, max_size_mb: int = 50) -> Tuple[str, str]:
    """Process audio with size limits and proper error handling"""
    try:
        # Check file size before decoding
        estimated_size = len(audio_data) * 3 / 4  # Base64 to bytes ratio
        if estimated_size > max_size_mb * 1024 * 1024:
            return None, f"File too large. Max size: {max_size_mb}MB"
        
        # Decode base64
        audio_bytes = base64.b64decode(audio_data)
        
        # Create temp file with proper cleanup
        with tempfile.NamedTemporaryFile(delete=True, suffix=".wav") as temp_file:
            temp_file.write(audio_bytes)
            temp_file.flush()
            
            # Process audio
            return transcribe_audio(temp_file.name)
            
    except Exception as e:
        logger.error(f"Audio processing error: {e}")
        return None, f"Error: {str(e)}"

def anonymize_text(text: str) -> str:
    """Remove personal information from text"""
    # Remove phone numbers
    text = re.sub(r'\b\d{10,11}\b', '[PHONE]', text)
    # Remove email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
    # Remove common names (basic implementation)
    common_names = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Phan', 'Vũ', 'Võ', 'Đặng', 'Bùi']
    for name in common_names:
        text = re.sub(rf'\b{name}\s+\w+\b', '[NAME]', text)
    return text

def encrypt_text(text: str, key: str = "counseling_key") -> str:
    """Simple encryption for text"""
    key_hash = hashlib.sha256(key.encode()).digest()
    encrypted = bytearray()
    for i, byte in enumerate(text.encode()):
        encrypted.append(byte ^ key_hash[i % len(key_hash)])
    return encrypted.hex()

def decrypt_text(encrypted_hex: str, key: str = "counseling_key") -> str:
    """Simple decryption for text"""
    key_hash = hashlib.sha256(key.encode()).digest()
    encrypted = bytes.fromhex(encrypted_hex)
    decrypted = bytearray()
    for i, byte in enumerate(encrypted):
        decrypted.append(byte ^ key_hash[i % len(key_hash)])
    return decrypted.decode()

def mock_counseling_response(text: str) -> str:
    """Mock counseling response for demo purposes"""
    responses = [
        "Tôi hiểu cảm xúc của bạn. Hãy chia sẻ thêm về tình huống này.",
        "Điều này có vẻ rất khó khăn. Bạn đã thử cách nào để đối phó chưa?",
        "Cảm ơn bạn đã tin tưởng chia sẻ. Hãy cùng tìm hiểu sâu hơn về vấn đề này.",
        "Tôi cảm nhận được sự lo lắng của bạn. Hãy thử hít thở sâu và chia sẻ thêm.",
        "Đây là một bước tích cực khi bạn tìm kiếm sự giúp đỡ. Hãy nói thêm về cảm xúc của bạn."
    ]
    return responses[hash(text) % len(responses)]

def call_counseling_api(text: str, api_url: str, api_key: str, encrypt_data: bool = False, anonymize: bool = False) -> Tuple[str, str]:
    """Call counseling API"""
    try:
        # For demo, use mock response
        if api_url == "https://demo.counseling-api.com":
            response_text = mock_counseling_response(text)
            return response_text, "Success"
        
        # Process text
        processed_text = text
        if anonymize:
            processed_text = anonymize_text(processed_text)
        if encrypt_data:
            processed_text = encrypt_text(processed_text, api_key)
        
        # Make API call
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        data = {"message": processed_text, "encrypted": encrypt_data}
        
        response = requests.post(api_url, json=data, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        response_text = result.get("response", "No response received")
        
        # Decrypt if needed
        if encrypt_data and result.get("encrypted", False):
            response_text = decrypt_text(response_text, api_key)
        
        return response_text, "Success"
        
    except Exception as e:
        logger.error(f"API call error: {e}")
        return None, f"API Error: {str(e)}"

def text_to_speech(text: str) -> Optional[bytes]:
    """Convert text to speech using gTTS"""
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang='vi', slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer.getvalue()
    except ImportError:
        logger.warning("gTTS not available for TTS")
        return None
    except Exception as e:
        logger.error(f"TTS error: {e}")
        return None

def main():
    """Main counseling app - Optimized UI"""
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'api_url' not in st.session_state:
        st.session_state.api_url = "https://demo.counseling-api.com"
    if 'api_key' not in st.session_state:
        st.session_state.api_key = "demo_key_123"
    if 'is_processing' not in st.session_state:
        st.session_state.is_processing = False
    if 'pending_audio' not in st.session_state:
        st.session_state.pending_audio = None
    if 'processing_uploaded_audio' not in st.session_state:
        st.session_state.processing_uploaded_audio = False
    if 'upload_counter' not in st.session_state:
        st.session_state.upload_counter = 0
    
    # Check for audio data in URL parameters
    if 'audio_data' in st.query_params:
        audio_data = st.query_params['audio_data']
        if audio_data and not st.session_state.pending_audio:
            st.session_state.pending_audio = audio_data
            # Clear the URL parameter
            st.query_params.clear()
    
    # Apply CSS
    st.markdown(CSS_STYLES, unsafe_allow_html=True)
    
    # Main layout - Header only
    st.markdown('''
    <div style="display: flex; flex-direction: column; overflow: hidden;">
        <div class="chat-title">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 24px;">🧑‍⚕️</span>
                <span>AI Tư vấn Tâm lý</span>
            </div>
            <div style="display: flex; flex-direction: column; align-items: flex-end; font-size: 12px; line-height: 1.2;">
                <div style="font-weight: 600; font-size: 14px;">Chuyên gia tâm lý</div>
                <div>Nguyễn Minh Quang, Nguyễn Ngọc Bách, Nguyễn Vũ Dũng</div>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Display chat messages
    
    # Clear session button
    if st.sidebar.button("🗑️ Clear All Messages"):
        st.session_state.messages = []
        st.session_state.processing_uploaded_audio = False
        st.rerun()
    
    # Test message display
    if len(st.session_state.messages) == 0:
        st.markdown("**No messages yet. Upload an audio file to start!**")
    
    # Display each message with structure: chat-container -> stLayoutWrapper -> stChatMessage
    for i, message in enumerate(st.session_state.messages):
        
        # Create a container that will be styled as chat-container
        with st.container():
            # Add CSS class to this container to make it look like chat-container
            st.markdown(f'''
            <style>
            .stContainer:has(.stChatMessage) {{
                background: #ffffff !important;
                min-height: 60px !important;
                padding: 15px 20px !important;
                border-left: 1px solid #e0e0e0 !important;
                border-right: 1px solid #e0e0e0 !important;
                border-bottom: 1px solid #f0f0f0 !important;
                margin-bottom: 2px !important;
            }}
            </style>
            ''', unsafe_allow_html=True)
            
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(message["content"])
                    
                    # Show audio if available
                    if "audio" in message and message["audio"]:
                        st.audio(message["audio"], format="audio/wav")
    
    # Auto-scroll to bottom after displaying messages
    st.markdown('''
    <script>
    // Auto-scroll to bottom of the page to show latest messages
    setTimeout(function() {
        window.scrollTo({
            top: document.body.scrollHeight,
            behavior: 'smooth'
        });
    }, 100);
    </script>
    ''', unsafe_allow_html=True)
    
    # Typing indicator
    if st.session_state.is_processing:
        with st.container():
            st.markdown('''
            <div class="typing-indicator">
                <div class="message-avatar">AI</div>
                <div class="typing-bubble">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
    
    # Simple input area (file uploader will be positioned with CSS)
    st.markdown('''
        <div class="input-area">
            <div class="input-container" id="inputContainer">
                <input type="text" class="input-field" placeholder="Nhập tin nhắn của bạn..." id="messageInput">
            </div>
            <button class="send-button" id="sendBtn">Gửi</button>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    
    # JavaScript for file upload using components.v1.html
    st.components.v1.html('''
    <script>
    function showLoadingScreen() {
        // Create loading overlay
        const loadingOverlay = document.createElement('div');
        loadingOverlay.id = 'loadingOverlay';
        loadingOverlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            color: white;
            font-family: Arial, sans-serif;
        `;
        
        loadingOverlay.innerHTML = `
            <div style="text-align: center;">
                <div style="font-size: 24px; margin-bottom: 20px;">🎤</div>
                <div style="font-size: 18px; margin-bottom: 10px;">Đang xử lý audio...</div>
                <div style="font-size: 14px; opacity: 0.8;">Vui lòng chờ trong giây lát</div>
                <div style="margin-top: 20px;">
                    <div style="width: 40px; height: 40px; border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto;"></div>
                </div>
            </div>
            <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        `;
        
        document.body.appendChild(loadingOverlay);
    }
    
    function hideLoadingScreen() {
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            loadingOverlay.remove();
        }
    }
    
    function showError(message) {
        // Create error overlay
        const errorOverlay = document.createElement('div');
        errorOverlay.id = 'errorOverlay';
        errorOverlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            color: white;
            font-family: Arial, sans-serif;
        `;
        
        errorOverlay.innerHTML = `
            <div style="text-align: center; background: #e74c3c; padding: 30px; border-radius: 10px; max-width: 400px;">
                <div style="font-size: 24px; margin-bottom: 20px;">❌</div>
                <div style="font-size: 18px; margin-bottom: 20px;">${message}</div>
                <button onclick="this.parentElement.parentElement.remove()" style="background: #c0392b; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-size: 16px;">Đóng</button>
            </div>
        `;
        
        document.body.appendChild(errorOverlay);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (errorOverlay.parentNode) {
                errorOverlay.remove();
            }
        }, 5000);
    }
    
    
    function sendMessage() {
        const input = document.getElementById('messageInput');
        if (input.value.trim()) {
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: input.value,
                key: 'text_input_from_js'
            }, '*');
            input.value = '';
        }
    }
    
    // Listen for messages from Streamlit to hide loading screen
    window.addEventListener('message', function(event) {
        if (event.data && event.data.type === 'streamlit:processingComplete') {
            hideLoadingScreen();
        } else if (event.data && event.data.type === 'streamlit:processingError') {
            hideLoadingScreen();
            showError(event.data.message || 'Có lỗi xảy ra khi xử lý audio');
        }
    });
    
    // Listen for audio upload messages
    window.addEventListener('message', function(event) {
        if (event.data && event.data.type === 'streamlit:audioUpload') {
            // LOG AUDIO CONTENT (TEXT TRANSCRIPTION) - Client side
            console.log('🎤 AUDIO CONTENT (TEXT TRANSCRIPTION) - Client side:');
            console.log('📝 Audio file uploaded, waiting for transcription...');
            console.log('📝 Expected audio content: [Will be displayed after processing]');
            console.log('🎤 END AUDIO CONTENT (TEXT TRANSCRIPTION) - Client side');
            
            // The audio data will be processed by Python side
    });
    
    
    // Add event listeners with delay to ensure DOM is ready
    setTimeout(function() {
        
        // Try to find elements in parent document
        const parentDoc = window.parent.document;
        
        const messageInput = parentDoc.getElementById('messageInput');
        if (messageInput) {
            messageInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') sendMessage();
            });
        }
        
        const sendBtn = parentDoc.getElementById('sendBtn');
        if (sendBtn) {
            sendBtn.addEventListener('click', sendMessage);
        }
    }, 1000);
    </script>
    ''', height=0)
    
    # File uploader for audio files - Now integrated into footer
    uploaded_audio = st.file_uploader(
        "", 
        type=['wav', 'mp3', 'flac', 'm4a', 'ogg'], 
        key=f"audio_uploader_{st.session_state.get('upload_counter', 0)}",
        help=None
    )
    
    # Handle input from JavaScript (hidden inputs for communication)
    js_text_input = st.text_input("Hidden Text Input", key="text_input_from_js", label_visibility="collapsed")
    js_audio_input = st.text_input("Hidden Audio Input", key="audio_input_from_js", label_visibility="collapsed")
    
    
    # Process text input (from input field only)
    if js_text_input:
        user_message = js_text_input
        st.session_state.messages.append({
            "role": "user", 
            "content": user_message,
            "timestamp": time.strftime("%H:%M")
        })
        st.session_state.is_processing = False
        st.rerun()
    
    # IMPROVED: Process pending audio with better error handling
    if st.session_state.pending_audio:
        audio_data = st.session_state.pending_audio
        st.session_state.pending_audio = None  # Clear pending audio
        
        
        # Use improved audio processing function
        transcription, status = process_audio_safely(audio_data, max_size_mb=50)
        
        if transcription:
            # LOG AUDIO CONTENT (TEXT TRANSCRIPTION)
            print("🎤 AUDIO CONTENT (TEXT TRANSCRIPTION) - Session State:")
            print(f"📝 Audio content extracted: \"{transcription}\"")
            print(f"📝 Audio content length: {len(transcription)} characters")
            print(f"📝 Audio content words: {len(transcription.split())} words")
            print("🎤 END AUDIO CONTENT (TEXT TRANSCRIPTION) - Session State")
            
            # Add transcription as user message
            st.session_state.messages.append({
                "role": "user", 
                "content": transcription,
                "timestamp": time.strftime("%H:%M")
            })
            st.session_state.is_processing = True
        else:
            st.error(status)
            print(f"❌ Transcription Error: {status}")
            
            st.session_state.is_processing = False
            
            # Send completion message to JavaScript
            st.components.v1.html('''
            <script>
            window.parent.postMessage({
                type: 'streamlit:processingComplete',
                message: 'Audio processing completed successfully'
            }, '*');
            </script>
            ''', height=0)
            
            st.rerun()
    
    # Process audio input with better error handling (for legacy compatibility)
    if js_audio_input:
        # Use improved audio processing function
        transcription, status = process_audio_safely(js_audio_input, max_size_mb=50)
        
        if transcription:
            # LOG AUDIO CONTENT (TEXT TRANSCRIPTION)
            print("🎤 AUDIO CONTENT (TEXT TRANSCRIPTION) - Legacy Audio Input:")
            print(f"📝 Audio content extracted: \"{transcription}\"")
            print(f"📝 Audio content length: {len(transcription)} characters")
            print(f"📝 Audio content words: {len(transcription.split())} words")
            print("🎤 END AUDIO CONTENT (TEXT TRANSCRIPTION) - Legacy Audio Input")
            
            # Add transcription as user message
            st.session_state.messages.append({
                "role": "user", 
                "content": transcription,
                "timestamp": time.strftime("%H:%M")
            })
            st.session_state.is_processing = True
        else:
            st.error(status)
            print(f"❌ Transcription Error: {status}")
            
            st.session_state.is_processing = False
            
            # Send completion message to JavaScript
            st.components.v1.html('''
            <script>
            window.parent.postMessage({
                type: 'streamlit:processingComplete',
                message: 'Audio processing completed successfully'
            }, '*');
            </script>
            ''', height=0)
            
            st.rerun()
    
    
    # Process uploaded audio file with better error handling
    if uploaded_audio and not st.session_state.get('processing_uploaded_audio', False):
        st.session_state.processing_uploaded_audio = True
        
        print(f"🎤 AUDIO UPLOAD DETECTED:")
        print(f"📁 File name: {uploaded_audio.name}")
        print(f"📊 File size: {uploaded_audio.size} bytes")
        print(f"📋 File type: {uploaded_audio.type}")
        
        # Show loading screen
        with st.spinner("🎤 Processing audio file..."):
            pass
        
        
        # Check file size before processing
        max_size_mb = 50
        if uploaded_audio.size > max_size_mb * 1024 * 1024:
            st.error(f"File too large. Max size: {max_size_mb}MB")
            st.session_state.processing_uploaded_audio = False
            st.rerun()
            return
        
        with tempfile.NamedTemporaryFile(delete=True, suffix=os.path.splitext(uploaded_audio.name)[1]) as temp_file:
            temp_file.write(uploaded_audio.read())
            temp_file.flush()
            print(f"💾 Temporary file created: {temp_file.name}")
            
            print("🔄 Starting transcription...")
            transcription, status = transcribe_audio(temp_file.name)
            print(f"📝 Transcription result: {transcription}")
            print(f"✅ Status: {status}")
            
            # Console.log for transcription process
            st.markdown(f'''
            <script>
            console.log("🔄 TRANSCRIPTION COMPLETED:");
            console.log("📝 Raw result: \\"{transcription}\\"");
            console.log("✅ Status: {status}");
            </script>
            ''', unsafe_allow_html=True)
            
            if transcription:
                # LOG AUDIO CONTENT (TEXT TRANSCRIPTION)
                print("🎤 AUDIO CONTENT (TEXT TRANSCRIPTION) - Uploaded File:")
                print(f"📝 Audio content extracted: \"{transcription}\"")
                print(f"📝 Audio content length: {len(transcription)} characters")
                print(f"📝 Audio content words: {len(transcription.split())} words")
                print("🎤 END AUDIO CONTENT (TEXT TRANSCRIPTION) - Uploaded File")
                
                
                # Add transcription as user message
                st.session_state.messages.append({
                    "role": "user", 
                    "content": transcription,
                    "timestamp": time.strftime("%H:%M")
                })
                
                
                
                # Continue with API call
                st.session_state.is_processing = True
            # Call AI API for response
            response, status = call_counseling_api(transcription, st.session_state.api_url, st.session_state.api_key)
            if response:
                audio_data = text_to_speech(response)
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response,
                    "timestamp": time.strftime("%H:%M"),
                    "audio": audio_data
                })
            else:
                st.error(status)
        
        st.session_state.is_processing = False
        st.session_state.processing_uploaded_audio = False
        
        # Increment upload counter to reset file uploader
        st.session_state.upload_counter += 1
        st.rerun()


if __name__ == "__main__":
    main()
