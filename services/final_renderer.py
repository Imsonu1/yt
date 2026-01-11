import subprocess
from utils.config import (
    BASE_VIDEO_PATH,
    FINAL_VIDEO_PATH,
    TEMP_AUDIO_PATH
)


def render_final():
    """
    Render final Shorts/Reels video.

    RULES:
    - Video loops infinitely
    - Audio controls duration
    - No manual -t
    - No burned text
    - Render-safe (Linux / Render)
    """

    ffmpeg_cmd = [
        "ffmpeg", "-y",

        # 🔁 Loop video forever
        "-stream_loop", "-1",
        "-i", BASE_VIDEO_PATH,

        # 🎧 Audio (master timeline)
        "-i", TEMP_AUDIO_PATH,

        # 📐 Force Shorts / Reels aspect ratio
        "-vf",
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920",

        # 🎯 Map streams
        "-map", "0:v:0",
        "-map", "1:a:0",

        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",

        # 🧠 THIS IS THE KEY
        "-shortest",

        FINAL_VIDEO_PATH
    ]

    subprocess.run(ffmpeg_cmd, check=True)
    return FINAL_VIDEO_PATH
