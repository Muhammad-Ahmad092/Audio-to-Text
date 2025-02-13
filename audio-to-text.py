import streamlit as st
from whisper import load_model
import os

# Load the Whisper model (ensure 'openai-whisper' is installed)
@st.cache_resource
def load_whisper_model():
    return load_model("base")  # Replace "base" with "tiny", "medium", etc.

model = load_whisper_model()

# Streamlit App Configuration
st.set_page_config(page_title="Audio-to-Text Converter", layout="centered", page_icon="🎤")

# Frontend - UI Design
st.title("🎤 Audio-to-Text Converter")
st.markdown(
    """
    Welcome to the **Audio-to-Text Converter**!  
    Effortlessly convert your audio files into text and subtitles.  

    🔹 **Features**:  
    - Generate a **Text File** and **Subtitle (SRT) File**.  
    - Supports multiple audio formats: `mp3`, `mp4`, `m4a`, `wav`.  
    """
)

def format_timestamp(seconds):
    """Format a timestamp in seconds to the SRT format: HH:MM:SS,ms."""
    milliseconds = int((seconds % 1) * 1000)
    seconds = int(seconds)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

# File Upload Section
st.header("📤 Upload Your Audio File")
uploaded_file = st.file_uploader("Choose an audio file", type=["mp3", "mp4", "m4a", "wav"])

if uploaded_file:
    # Display file details
    st.write(f"**Filename**: `{uploaded_file.name}`")
    file_size = len(uploaded_file.getvalue()) / (1024 * 1024)
    st.write(f"**File Size**: `{file_size:.2f} MB`")

    # Save uploaded file locally
    file_path = os.path.join("temp", uploaded_file.name)
    os.makedirs("temp", exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("File uploaded successfully! 🎉")

    # Transcription Button
    if st.button("🎙️ Convert Audio to Text"):
        with st.spinner("Transcription in progress... This might take a while ⏳"):
            # Transcribe audio using Whisper
            result = model.transcribe(file_path)

            # Extract transcription text and create output files
            transcription_text = result["text"]
            text_file_path = os.path.join("temp", "transcription.txt")
            subtitle_file_path = os.path.join("temp", "transcription.srt")

            # Save transcription to a text file
            with open(text_file_path, "w", encoding="utf-8") as text_file:
                text_file.write(transcription_text)

            # Save subtitles (SRT format)
            with open(subtitle_file_path, "w", encoding="utf-8") as srt_file:
                for segment in result["segments"]:
                    start = segment["start"]
                    end = segment["end"]
                    text = segment["text"]
                    srt_file.write(f"{segment['id'] + 1}\n")
                    srt_file.write(f"{format_timestamp(start)} --> {format_timestamp(end)}\n")
                    srt_file.write(f"{text}\n\n")

        # Output Section
        st.success("Transcription complete! ✅")
        st.balloons()

        # File download section
        st.subheader("📥 Download Your Files")
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📄 Download Text File",
                data=open(text_file_path, "r").read(),
                file_name="transcription.txt",
            )
        with col2:
            st.download_button(
                label="🎞️ Download Subtitle File",
                data=open(subtitle_file_path, "r").read(),
                file_name="transcription.srt",
            )
