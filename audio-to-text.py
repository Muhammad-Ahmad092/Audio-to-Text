import streamlit as st
import whisper
import tempfile
import os
import shutil
import requests
import zipfile

# Function to download and setup FFmpeg automatically
def setup_ffmpeg():
    ffmpeg_dir = os.path.join(os.getcwd(), "ffmpeg_bin")
    ffmpeg_path = os.path.join(ffmpeg_dir, "ffmpeg.exe")

    if not os.path.exists(ffmpeg_path):
        st.write("Downloading FFmpeg... ⏳")
        url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        zip_path = "ffmpeg.zip"

        with open(zip_path, "wb") as f:
            f.write(requests.get(url, stream=True).content)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall("ffmpeg_temp")

        extracted_dir = [d for d in os.listdir("ffmpeg_temp") if os.path.isdir(os.path.join("ffmpeg_temp", d))][0]
        shutil.move(os.path.join("ffmpeg_temp", extracted_dir, "bin"), ffmpeg_dir)

        os.remove(zip_path)
        shutil.rmtree("ffmpeg_temp")
        st.write("FFmpeg setup complete ✅")

    return ffmpeg_dir

ffmpeg_dir = setup_ffmpeg()
os.environ["PATH"] += os.pathsep + ffmpeg_dir

@st.cache_resource
def load_model():
    return whisper.load_model("small")

model = load_model()

# Custom CSS for styling
st.markdown(
    """
    <style>
        body {
            background-color: #1e1e1e;
            color: white;
            font-family: 'Arial', sans-serif;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 16px;
            margin: 10px 0;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }
        .uploaded-file-details {
            margin-top: 15px;
            font-size: 14px;
            color: #ddd;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Streamlit App Layout
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
    st.audio(uploaded_file, format="audio/mp3")
    file_size = uploaded_file.size / (1024 * 1024)
    st.markdown(
        f"""
        <div class="uploaded-file-details">
            <strong>Filename:</strong> {uploaded_file.name} <br>
            <strong>File Size:</strong> {file_size:.2f} MB
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Convert Audio to Text"):
        with st.spinner("Transcription in progress... This might take a while ⏳"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                temp_audio.write(uploaded_file.read())
                temp_audio_path = temp_audio.name

            result = model.transcribe(temp_audio_path)
            os.remove(temp_audio_path)

        st.success("Transcription Complete! 🎉")
        st.subheader("Transcription:")
        st.write(result["text"])
