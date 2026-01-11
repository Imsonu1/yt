import streamlit as st
import io

from services.video_fetcher import fetch_video
from services.final_renderer import render_final
from services.voice_generator import generate_ai_voice
from services.music_mixer import mix_audio
from services.subtitle_generator import generate_srt
from services.subtitle_muxer import embed_srt
from utils.audio import get_audio_duration
from utils import config

# ---------------- PAGE SETUP ----------------
st.set_page_config(page_title="Auto Shorts Generator")
st.title("🎬 Auto Shorts Generator")

# ---------------- SESSION STATE ----------------
if "video_bytes" not in st.session_state:
    st.session_state.video_bytes = None

if "srt_bytes" not in st.session_state:
    st.session_state.srt_bytes = None
# ------------------------------------------------


# ================= FORM (CRITICAL FIX) =================
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


# ================= GENERATION =================
if submitted:
    if not keyword or not script:
        st.error("Keyword and script required")
        st.stop()

    st.session_state.video_bytes = None
    st.session_state.srt_bytes = None

    original_script = script.strip()
    config.SCRIPT_TEXT = ""

    with st.spinner("📥 Fetching video..."):
        fetch_video(keyword)

    with st.spinner("🎙️ Generating voice..."):
        voice_path = generate_ai_voice(original_script)

    with st.spinner("🎵 Mixing background music..."):
        final_audio_path = mix_audio(voice_path, bg_music)

    with st.spinner("⏱️ Calculating audio duration..."):
        duration = get_audio_duration(final_audio_path)

    with st.spinner("💬 Generating subtitle track (CC)..."):
        srt_path = "/tmp/subtitles.srt"
        generate_srt(original_script, duration, srt_path)

    with st.spinner("🎬 Rendering final video..."):
        output_path = render_final()

    if embed_cc:
        with st.spinner("🧩 Embedding subtitles into video..."):
            cc_output = "/tmp/short_with_cc.mp4"
            output_path = embed_srt(output_path, srt_path, cc_output)

    # -------- READ FILES INTO MEMORY (NO PATH USE LATER) --------
    with open(output_path, "rb") as f:
        st.session_state.video_bytes = f.read()

    with open(srt_path, "rb") as f:
        st.session_state.srt_bytes = f.read()

    st.success("✅ Video generated successfully!")


# ================= OUTPUT / DOWNLOAD =================
if st.session_state.video_bytes:

    st.subheader("🎥 Preview")
    st.video(st.session_state.video_bytes)

    st.download_button(
        "⬇️ Download video",
        data=io.BytesIO(st.session_state.video_bytes),
        file_name="short.mp4",
        mime="video/mp4"
    )

if st.session_state.srt_bytes:
    st.download_button(
        "⬇️ Download subtitles (SRT)",
        data=io.BytesIO(st.session_state.srt_bytes),
        file_name="subtitles.srt",
        mime="text/plain"
    )
# -------------------------------------------------
