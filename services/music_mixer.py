import subprocess
import os
from utils.config import TEMP_AUDIO_PATH, BG_MUSIC_MAP


def mix_audio(voice_path, bg_choice):
    """
    Mix background music with voice using FFmpeg only.
    Returns path to final mixed audio.
    """

    # If no BG music, just return original voice
    if bg_choice == "None":
        return voice_path

    bg_path = BG_MUSIC_MAP.get(bg_choice)
    if not bg_path or not os.path.exists(bg_path):
        return voice_path

    output_audio = TEMP_AUDIO_PATH.replace(".wav", "_mixed.wav")

    cmd = [
        "ffmpeg", "-y",
        "-i", voice_path,
        "-i", bg_path,
        "-filter_complex",
        "[1:a]volume=0.15[a1];[0:a][a1]amix=inputs=2:duration=shortest",
        "-c:a", "aac",
        output_audio
    ]

    subprocess.run(cmd, check=True)
    return output_audio
