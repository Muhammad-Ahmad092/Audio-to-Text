import streamlit as st
import openai
import os

# Set your OpenAI API key (ensure this is secure in a production environment)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Add your key to Streamlit Cloud secrets or environment
openai.api_key = OPENAI_API_KEY

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

    # Transcription Button
    if st.button("🎙️ Convert Audio to Text"):
        with st.spinner("Transcription in progress... This might take a while ⏳"):
            try:
                # Send audio file to OpenAI Whisper API
                audio_file = open(uploaded_file.name, "rb")
                response = openai.Audio.transcribe("whisper-1", audio_file)
                transcription_text = response["text"]

                # Generate subtitles (SRT format)
                subtitle_text = ""
                for i, segment in enumerate(response.get("segments", [])):
                    start = segment["start"]
                    end = segment["end"]
                    text = segment["text"]
                    subtitle_text += (
                        f"{i + 1}\n"
                        f"{format_timestamp(start)} --> {format_timestamp(end)}\n"
                        f"{text}\n\n"
                    )

                # Output Section
                st.success("Transcription complete! ✅")
                st.balloons()

                # File download section
                st.subheader("📥 Download Your Files")
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="📄 Download Text File",
                        data=transcription_text,
                        file_name="transcription.txt",
                        mime="text/plain",
                    )
                with col2:
                    st.download_button(
                        label="🎞️ Download Subtitle File",
                        data=subtitle_text,
                        file_name="transcription.srt",
                        mime="text/plain",
                    )
            except Exception as e:
                st.error(f"An error occurred: {e}")
