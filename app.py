import streamlit as st
import uuid
import os
import tempfile
import threading
import logging

from services.video_fetcher import fetch_video
from services.final_renderer import render_final
from services.voice_generator import generate_ai_voice
from services.music_mixer import mix_audio
from services.subtitle_generator import generate_srt
from services.subtitle_muxer import embed_srt
from utils.audio import get_audio_duration
from utils import config

# ================= LOGGING =================
logging.basicConfig(level=logging.INFO)

# ================= ENV DETECTION =================
IS_CLOUD = os.getenv("K_SERVICE") is not None

# ================= CONFIG =================
GCS_BUCKET_NAME = "auto-shorts-output"
TMP_DIR = tempfile.gettempdir()
SRT_PATH = os.path.join(TMP_DIR, "subtitles.srt")
CC_OUTPUT_PATH = os.path.join(TMP_DIR, "short_with_cc.mp4")

# ---------------- PAGE SETUP ----------------
st.set_page_config(page_title="Auto Shorts Generator")
st.title("🎬 Auto Shorts Generator")

# ---------------- SESSION STATE ----------------
for key in ["video_path", "video_url", "srt_bytes", "status"]:
    if key not in st.session_state:
        st.session_state[key] = None


def upload_to_gcs(local_path: str, content_type: str) -> str:
    from google.cloud import storage

    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET_NAME)

    blob_name = f"shorts/{uuid.uuid4()}.mp4"
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(local_path, content_type=content_type)

    return blob.generate_signed_url(
        version="v4",
        expiration=3600,
        method="GET"
    )


def run_generation(keyword, script, bg_music, embed_cc):
    try:
        logging.info("Generation started")
        st.session_state.status = "Fetching video..."

        fetch_video(keyword)

        st.session_state.status = "Generating voice..."
        voice_path = generate_ai_voice(script)

        st.session_state.status = "Mixing audio..."
        final_audio_path = mix_audio(voice_path, bg_music)

        st.session_state.status = "Calculating duration..."
        duration = get_audio_duration(final_audio_path)

        st.session_state.status = "Generating subtitles..."
        generate_srt(script, duration, SRT_PATH)

        st.session_state.status = "Rendering video..."
        output_path = render_final()

        if embed_cc:
            st.session_state.status = "Embedding subtitles..."
            output_path = embed_srt(output_path, SRT_PATH, CC_OUTPUT_PATH)

        if IS_CLOUD:
            st.session_state.status = "Uploading to cloud..."
            st.session_state.video_url = upload_to_gcs(
                output_path, "video/mp4"
            )
        else:
            st.session_state.video_path = output_path

        with open(SRT_PATH, "rb") as f:
            st.session_state.srt_bytes = f.read()

        st.session_state.status = "DONE"
        logging.info("Generation finished successfully")

    except Exception as e:
        logging.exception("Generation failed")
        st.session_state.status = f"ERROR: {e}"


# ================= FORM =================
with st.form("generate_form"):
    keyword = st.text_input("Video keyword")
    script = st.text_area("Paste your script")

    bg_music = st.selectbox(
        "Background music",
        ["None", "Calm", "Ocean", "Motivation"]
    )

    embed_cc = st.checkbox(
        "Embed subtitles (CC) inside video (YouTube)",
        value=False
    )

    submitted = st.form_submit_button("Generate")


# ================= GENERATION TRIGGER =================
if submitted:
    if not keyword or not script:
        st.error("Keyword and script required")
        st.stop()

    st.session_state.video_path = None
    st.session_state.video_url = None
    st.session_state.srt_bytes = None
    st.session_state.status = "Starting..."

    threading.Thread(
        target=run_generation,
        args=(keyword, script.strip(), bg_music, embed_cc),
        daemon=True
    ).start()

    st.info("🎬 Video generation started. Please wait...")


# ================= STATUS =================
if st.session_state.status and st.session_state.status != "DONE":
    st.warning(st.session_state.status)

# ================= OUTPUT =================
if st.session_state.video_path:
    st.subheader("🎬 Preview")
    st.video(st.session_state.video_path)

if st.session_state.video_url:
    st.subheader("⬇️ Download")
    st.markdown(
        f"### 🎬 [Download Video]({st.session_state.video_url})"
    )

if st.session_state.srt_bytes:
    st.download_button(
        "⬇️ Download subtitles (SRT)",
        data=st.session_state.srt_bytes,
        file_name="subtitles.srt",
        mime="text/plain"
    )

if st.session_state.status == "DONE":
    st.success("✅ Video ready!")
