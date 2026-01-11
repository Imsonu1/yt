import streamlit as st
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
if "video_path" not in st.session_state:
    st.session_state.video_path = None

if "srt_path" not in st.session_state:
    st.session_state.srt_path = None
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

    # 🔹 Original script (Hindi / Hinglish allowed)
    original_script = script.strip()

    # 🔹 Disable burned text overlay completely (SRT only)
    config.SCRIPT_TEXT = ""

    st.write("📥 Fetching video...")
    fetch_video(keyword)

    st.write("🎙️ Generating voice...")
    voice_path = generate_ai_voice(original_script)

    st.write("🎵 Mixing background music...")
    final_audio_path = mix_audio(voice_path, bg_music)

    st.write("⏱️ Calculating audio duration...")
    duration = get_audio_duration(final_audio_path)

    st.write("💬 Generating subtitle track (CC)...")
    srt_path = "temp/subtitles.srt"
    generate_srt(original_script, duration, srt_path)

    st.write("🎬 Rendering final video...")
    output = render_final()

    # 🔹 Optional: embed CC track into MP4 (YouTube compatible)
    if embed_cc:
        st.write("🧩 Embedding subtitles into video...")
        cc_output = "temp/short_with_cc.mp4"
        output = embed_srt(output, srt_path, cc_output)

    # ---------------- SAVE OUTPUT ----------------
    st.session_state.video_path = output
    st.session_state.srt_path = srt_path

    st.success("✅ Done!")

# ---------------- DOWNLOAD SECTION ----------------
if st.session_state.video_path:
    st.download_button(
        "⬇️ Download video",
        open(st.session_state.video_path, "rb"),
        file_name="short.mp4",
        mime="video/mp4"
    )

if st.session_state.srt_path:
    st.download_button(
        "⬇️ Download subtitles (SRT)",
        open(st.session_state.srt_path, "rb"),
        file_name="subtitles.srt",
        mime="text/plain"
    )
# -------------------------------------------------
