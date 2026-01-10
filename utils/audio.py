import subprocess
import json


def get_audio_duration(audio_path):
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json",
        audio_path
    ]

    result = subprocess.run(
        cmd, capture_output=True, text=True, check=True
    )

    data = json.loads(result.stdout)
    return float(data["format"]["duration"])
