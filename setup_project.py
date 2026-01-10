import os

BASE = r"E:\yt"


def make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# ------------------ CREATE FOLDERS ------------------
make_dir(BASE)
make_dir(os.path.join(BASE, "assets"))
make_dir(os.path.join(BASE, "assets", "music"))
make_dir(os.path.join(BASE, "temp"))
make_dir(os.path.join(BASE, "services"))
make_dir(os.path.join(BASE, "utils"))

# ------------------ CREATE FILES ------------------

write_file(os.path.join(BASE, "requirements.txt"),
           """streamlit
requests
gtts
moviepy
""")

write_file(os.path.join(BASE, "utils", "config.py"),
           r"""
import os

BASE_DIR = r"E:\yt"

ASSETS_DIR = os.path.join(BASE_DIR, "assets")
MUSIC_DIR = os.path.join(ASSETS_DIR, "music")
TEMP_DIR = os.path.join(BASE_DIR, "temp")

os.makedirs(MUSIC_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

VIDEO_PATH = os.path.join(TEMP_DIR, "video.mp4")
VOICE_PATH = os.path.join(TEMP_DIR, "voice.mp3")
FINAL_VIDEO_PATH = os.path.join(TEMP_DIR, "final.mp4")

VIDEO_DURATION = 30

BG_MUSIC_MAP = {
    "None": None,
    "Calm": os.path.join(MUSIC_DIR, "calm.mp3"),
    "Ocean": os.path.join(MUSIC_DIR, "ocean.mp3"),
    "Motivation": os.path.join(MUSIC_DIR, "motivation.mp3"),
}
""")

write_file(os.path.join(BASE, "services", "video_fetcher.py"),
           """
import requests
from utils.config import VIDEO_PATH

PIXABAY_API_KEY = "PUT_YOUR_PIXABAY_KEY_HERE"

def fetch_video(keyword):
    url = "https://pixabay.com/api/videos/"
    params = {
        "key": PIXABAY_API_KEY,
        "q": keyword,
        "orientation": "vertical",
        "per_page": 3,
    }

    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()

    if not data["hits"]:
        raise Exception("No video found")

    video_url = data["hits"][0]["videos"]["medium"]["url"]
    with open(VIDEO_PATH, "wb") as f:
        f.write(requests.get(video_url).content)
""")

write_file(os.path.join(BASE, "services", "voice_generator.py"),
           """
from gtts import gTTS
import shutil
from utils.config import VOICE_PATH

def generate_ai_voice(text, lang="hi"):
    gTTS(text=text, lang=lang).save(VOICE_PATH)

def save_uploaded_voice(uploaded_file):
    with open(VOICE_PATH, "wb") as f:
        shutil.copyfileobj(uploaded_file, f)
""")

write_file(os.path.join(BASE, "services", "music_mixer.py"),
           """
from moviepy.editor import AudioFileClip, CompositeAudioClip
from utils.config import BG_MUSIC_MAP

def mix_audio(voice_path, bg_choice):
    voice = AudioFileClip(voice_path)

    if bg_choice == "None":
        return voice

    bg = AudioFileClip(BG_MUSIC_MAP[bg_choice]).volumex(0.1)
    return CompositeAudioClip([bg, voice])
""")

write_file(os.path.join(BASE, "services", "video_renderer.py"),
           """
from moviepy.editor import VideoFileClip
from utils.config import VIDEO_PATH, FINAL_VIDEO_PATH, VIDEO_DURATION

def render_video(audio_clip):
    video = VideoFileClip(VIDEO_PATH)

    if video.duration > VIDEO_DURATION:
        video = video.subclip(0, VIDEO_DURATION)
    else:
        video = video.loop(duration=VIDEO_DURATION)

    final = video.set_audio(audio_clip)
    final.write_videofile(
        FINAL_VIDEO_PATH,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        threads=2
    )
    return FINAL_VIDEO_PATH
""")

write_file(os.path.join(BASE, "app.py"),
           """
import streamlit as st
from services.video_fetcher import fetch_video
from services.voice_generator import generate_ai_voice, save_uploaded_voice
from services.music_mixer import mix_audio
from services.video_renderer import render_video
from utils.config import VOICE_PATH

st.set_page_config(page_title="Auto Short Video Generator")

st.title("🎬 Auto Short Video Generator")

keyword = st.text_input("Video keyword")
script = st.text_area("Paste your script")

voice_type = st.radio("Voice option", ["AI Voice", "Upload My Voice"])
uploaded = None
if voice_type == "Upload My Voice":
    uploaded = st.file_uploader("Upload voice (mp3/wav)", type=["mp3", "wav"])

bg_music = st.selectbox("Background music", ["None", "Calm", "Ocean", "Motivation"])

if st.button("🚀 Generate Video"):
    if not keyword or not script:
        st.error("Keyword and script are required")
    else:
        st.write("Fetching video...")
        fetch_video(keyword)

        st.write("Generating voice...")
        if voice_type == "AI Voice":
            generate_ai_voice(script)
        else:
            save_uploaded_voice(uploaded)

        st.write("Mixing audio...")
        audio = mix_audio(VOICE_PATH, bg_music)

        st.write("Rendering video...")
        output = render_video(audio)

        st.success("Video ready!")
        st.download_button("⬇️ Download Video", open(output, "rb"), "short_video.mp4")
""")

print("✅ SETUP COMPLETE: folders + files created in E:\\yt")
