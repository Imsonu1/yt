import subprocess
import os
from utils.config import (
    BASE_VIDEO_PATH,
    TEMP_AUDIO_PATH,
)

# ✅ Cloud Run writable directory
TMP_DIR = "/tmp"
FINAL_VIDEO_PATH = os.path.join(TMP_DIR, "final_short.mp4")


def render_final():
    """
    Ensures:
    - Video always matches audio duration
    - Short video loops cleanly
    - Long video trims cleanly
    - Cloud Run safe (/tmp only)
    """

    # ---------------- GET AUDIO DURATION ----------------
    duration_cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        TEMP_AUDIO_PATH
    ]

    duration = subprocess.check_output(duration_cmd).decode().strip()

    # ---------------- FFMPEG COMMAND ----------------
    ffmpeg_cmd = [
        "ffmpeg", "-y",

        # 🔁 Loop base video infinitely
        "-stream_loop", "-1",
        "-i", BASE_VIDEO_PATH,

        # 🎧 Final mixed voice audio
        "-i", TEMP_AUDIO_PATH,

        # 📐 Vertical format for Shorts/Reels
        "-vf",
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920",

        # 🎯 Map streams
        "-map", "0:v:0",
        "-map", "1:a:0",

        # 🎥 Video + Audio codecs
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",

        # ⏱️ Cut video exactly to audio duration
        "-t", duration,

        FINAL_VIDEO_PATH
    ]

    subprocess.run(ffmpeg_cmd, check=True)

    # ✅ Always return a /tmp path
    return FINAL_VIDEO_PATH
