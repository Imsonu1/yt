import subprocess
from utils.config import (
    BASE_VIDEO_PATH,
    FINAL_VIDEO_PATH,
    TEMP_AUDIO_PATH
)
from utils.audio import get_audio_duration
from utils import config

FONT_PATH = "E:/yt/assets/fonts/NotoSansDevanagari-Regular.ttf".replace(
    ":", "\\:")


def render_final():
    text = config.SCRIPT_TEXT.strip()

    # ❌ Burned text NOT recommended (keep empty in production)
    draw = (
        "drawtext="
        f"fontfile={FONT_PATH}:"
        f"text='{text}':"
        "fontsize=h*0.07:"
        "fontcolor=yellow:"
        "box=1:"
        "boxcolor=black@0.9:"
        "boxborderw=h*0.012:"
        "x=(w-text_w)/2:"
        "y=h*0.12"
    ) if text else "null"

    # 🔑 MASTER DURATION = AUDIO
    duration = round(get_audio_duration(TEMP_AUDIO_PATH), 2)

    ffmpeg_cmd = [
        "ffmpeg", "-y",

        # 🔁 LOOP VIDEO
        "-stream_loop", "-1",
        "-i", BASE_VIDEO_PATH,

        # 🎧 AUDIO
        "-i", TEMP_AUDIO_PATH,

        # 📐 VIDEO FILTER
        "-vf",
        (
            "scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920,"
            f"{draw}"
        ),

        # 🎯 FORCE EXACT DURATION (THIS IS THE FIX)
        "-t", str(duration),

        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",

        FINAL_VIDEO_PATH
    ]

    subprocess.run(ffmpeg_cmd, check=True)
    return FINAL_VIDEO_PATH
