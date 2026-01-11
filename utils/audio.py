import subprocess
import json
import os


def get_audio_duration(audio_path, fallback=15.0):
    """
    Safe audio duration reader for Render / cloud
    - Never crashes the app
    - Falls back if ffprobe fails
    """

    if not os.path.exists(audio_path):
        return fallback

    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "json",
            audio_path
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        data = json.loads(result.stdout)
        duration = float(data["format"]["duration"])

        # Sanity guard
        if duration <= 0:
            return fallback

        return duration

    except Exception:
        # Render-safe fallback
        return fallback
