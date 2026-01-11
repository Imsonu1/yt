import streamlit as st
from services.video_fetcher import fetch_video
from services.final_renderer import render_final
from services.voice_generator import generate_ai_voice
from services.music_mixer import mix_audio
from services.subtitle_generator import generate_srt
from services.subtitle_muxer import embed_srt
from utils.audio import get_audio_duration
from utils import config

st.set_page_config(page_title="Auto Shorts Generator")
st.title("🎬 Auto Shorts Generator")

# ---------------- SESSION STATE ----------------
if "video_path" not in st.session_state:
    st.session_state.video_path = None

if "srt_path" not in st.session_state:
    st.session_state.srt_path = None
# ------------------------------------------------

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

if st.button("Generate"):
    if not keyword or not script.strip():
        st.error("Keyword and script required")
        st.stop()

    # Original script for voice + subtitles
    original_script = script.strip()

    # HARD disable burned captions forever
    config.SCRIPT_TEXT = ""

    st.write("📥 Fetching video...")
    fetch_video(keyword)

    st.write("🎙️ Generating voice...")
    voice_path = generate_ai_voice(original_script)

    st.write("🎵 Mixing background music...")
    final_audio_path = mix_audio(voice_path, bg_music)

    # ✅ Render-safe duration
    duration = get_audio_duration(final_audio_path)

    st.write("💬 Generating subtitle track (CC)...")
    srt_path = "E:/yt/temp/subtitles.srt"
    generate_srt(original_script, duration, srt_path)

    st.write("🎬 Rendering final video...")
    output = render_final()

    if embed_cc:
        st.write("🧩 Embedding subtitle track...")
        cc_output = "E:/yt/temp/short_with_cc.mp4"
        output = embed_srt(output, srt_path, cc_output)

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
