import os
import logging
import streamlit as st
from pathlib import Path

from services.video_fetcher import fetch_video
from services.voice_generator import generate_ai_voice
from services.audio_mixer import mix_audio
from services.subtitle_generator import generate_srt
from services.video_renderer import render_final
from services.subtitle_embedder import embed_srt
from services.utils import get_audio_duration

# ================= CONFIG =================
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

BASE_VIDEO_PATH = OUTPUT_DIR / "base_video.mp4"
VOICE_PATH = OUTPUT_DIR / "voice.mp3"
FINAL_AUDIO_PATH = OUTPUT_DIR / "final_audio.mp3"
SRT_PATH = OUTPUT_DIR / "subtitles.srt"
FINAL_VIDEO_PATH = OUTPUT_DIR / "final_video.mp4"
FINAL_CC_VIDEO_PATH = OUTPUT_DIR / "final_cc_video.mp4"

logging.basicConfig(level=logging.INFO)

# ================= UI =================
st.set_page_config(page_title="Auto Shorts Generator", layout="centered")

st.title("🎬 Auto Shorts Generator")

keyword = st.text_input("Video keyword", placeholder="nature, hills")
script = st.text_area("Paste your script", height=150)

bg_music = st.selectbox(
    "Background music",
    ["None", "Calm", "Ocean"]
)

embed_cc = st.checkbox(
    "Embed subtitles (CC) inside video (YouTube)", value=True)

generate = st.button("Generate")

# ================= STATE =================
if "video_ready" not in st.session_state:
    st.session_state.video_ready = False

if "video_path" not in st.session_state:
    st.session_state.video_path = None

# ================= LOGIC =================


def generate_video():
    st.info("📥 Fetching stock video...")
    fetch_video(keyword, str(BASE_VIDEO_PATH))

    st.info("🎙 Generating voice...")
    generate_ai_voice(script, str(VOICE_PATH))

    st.info("🎵 Mixing audio...")
    mix_audio(str(VOICE_PATH), bg_music, str(FINAL_AUDIO_PATH))

    duration = get_audio_duration(str(FINAL_AUDIO_PATH))

    st.info("📝 Generating subtitles...")
    generate_srt(script, duration, str(SRT_PATH))

    st.info("🎞 Rendering video...")
    render_final(
        base_video=str(BASE_VIDEO_PATH),
        audio=str(FINAL_AUDIO_PATH),
        output=str(FINAL_VIDEO_PATH)
    )

    final_output = FINAL_VIDEO_PATH

    if embed_cc:
        st.info("🔤 Embedding subtitles...")
        embed_srt(
            video=str(FINAL_VIDEO_PATH),
            srt=str(SRT_PATH),
            output=str(FINAL_CC_VIDEO_PATH)
        )
        final_output = FINAL_CC_VIDEO_PATH

    st.session_state.video_path = str(final_output)
    st.session_state.video_ready = True


# ================= RUN =================
if generate:
    if not keyword or not script:
        st.error("Keyword and script are required")
        st.stop()

    st.session_state.video_ready = False
    st.session_state.video_path = None

    with st.spinner("⏳ Generating video. Please wait..."):
        generate_video()

# ================= OUTPUT =================
if st.session_state.video_ready:
    st.success("✅ Video generated successfully!")

    st.video(st.session_state.video_path)

    with open(st.session_state.video_path, "rb") as f:
        st.download_button(
            "⬇️ Download video",
            f,
            file_name="short_video.mp4",
            mime="video/mp4"
        )
