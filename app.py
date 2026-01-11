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

if "generated" not in st.session_state:
    st.session_state.generated = False
# ------------------------------------------------

# ---------------- UI INPUTS ----------------
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
# -------------------------------------------

if st.button("Generate"):
    if not keyword or not script:
        st.error("Keyword and script required")
        st.stop()

    # Reset old outputs
    st.session_state.video_bytes = None
    st.session_state.srt_bytes = None
    st.session_state.generated = False

    # Original script
    original_script = script.strip()

    # Disable burned text overlay
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

    # ---------------- READ FILES INTO MEMORY ----------------
    with open(output_path, "rb") as f:
        st.session_state.video_bytes = f.read()

    with open(srt_path, "rb") as f:
        st.session_state.srt_bytes = f.read()

    st.session_state.generated = True
    st.success("✅ Video generated successfully!")

# ---------------- OUTPUT SECTION ----------------
if st.session_state.generated:

    st.subheader("🎥 Preview")
    st.video(st.session_state.video_bytes)

    st.download_button(
        "⬇️ Download video",
        data=st.session_state.video_bytes,
        file_name="short.mp4",
        mime="video/mp4",
        key="download_video"
    )

    st.download_button(
        "⬇️ Download subtitles (SRT)",
        data=st.session_state.srt_bytes,
        file_name="subtitles.srt",
        mime="text/plain",
        key="download_srt"
    )
# -------------------------------------------------
