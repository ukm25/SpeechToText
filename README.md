# Vietnamese Speech-to-Text

A simple web application that converts Vietnamese speech to text using OpenAI's Whisper model.

## Features

- 🎥 **Video Upload**: Support for MP4, AVI, MOV, MKV, WebM formats
- 🎯 **Whisper Model**: OpenAI's state-of-the-art speech recognition
- 📝 **Text Processing**: Automatic punctuation and capitalization
- 💾 **Download**: Export transcription as TXT file
- ⚡ **Chunking**: Handles long videos (>30 seconds)

## Usage

1. Upload a video file (max 10 minutes, 100MB)
2. Click "Transcribe Video"
3. Wait for processing
4. Download the result

## Technical Details

- **Model**: OpenAI Whisper Small
- **Framework**: Streamlit
- **Audio Processing**: Librosa, PyDub
- **Deployment**: Render

## Local Development

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Deployment

This app is configured for deployment on Render with the following files:
- `render.yaml` - Render service configuration
- `Procfile` - Process definition
- `runtime.txt` - Python version specification