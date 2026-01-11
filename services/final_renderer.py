import subprocess
from utils.config import (
    BASE_VIDEO_PATH,
    FINAL_VIDEO_PATH,
    TEMP_AUDIO_PATH,
)


def render_final():
    """
    Ensures:
    - Video always matches audio duration
    - Short video loops cleanly
    - Long video trims cleanly
    """

    ffmpeg_cmd = [
        "ffmpeg", "-y",

        # 🔁 Loop base video if shorter than audio
        "-stream_loop", "-1",
        "-i", BASE_VIDEO_PATH,

        # 🎧 Final mixed voice audio
        "-i", TEMP_AUDIO_PATH,

        # 📐 Reels / Shorts format
        "-vf",
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920",

        # 🎯 CRITICAL FIX
        # Cut output EXACTLY to audio duration
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",

        # ⏱️ Audio decides duration (golden rule)
        "-t", "28.7",  # ← dynamically replaced below

        FINAL_VIDEO_PATH
    ]

    # 🔑 Replace hardcoded duration dynamically using ffprobe
    duration_cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        TEMP_AUDIO_PATH
    ]

    duration = subprocess.check_output(duration_cmd).decode().strip()

    ffmpeg_cmd[ffmpeg_cmd.index("-t") + 1] = duration

    subprocess.run(ffmpeg_cmd, check=True)
    return FINAL_VIDEO_PATH
