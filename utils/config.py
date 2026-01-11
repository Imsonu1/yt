import os
import tempfile

# =========================
# BASE DIRECTORY (READ-ONLY OK)
# =========================

BASE_DIR = os.getcwd()   # OK for assets (read-only)

# =========================
# ASSETS (READ-ONLY)
# =========================

ASSETS_DIR = os.path.join(BASE_DIR, "assets")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
MUSIC_DIR = os.path.join(ASSETS_DIR, "music")

# =========================
# TEMP DIRECTORY (WRITE ONLY HERE)
# Works on Windows + Linux + Cloud Run
# =========================

TEMP_DIR = tempfile.gettempdir()

# =========================
# VIDEO PIPELINE PATHS
# =========================

BASE_VIDEO_PATH = os.path.join(TEMP_DIR, "base_video.mp4")
TEXT_VIDEO_PATH = os.path.join(TEMP_DIR, "text_video.mp4")
TEMP_AUDIO_PATH = os.path.join(TEMP_DIR, "voice_temp.wav")
VOICE_PATH = os.path.join(TEMP_DIR, "voice.mp3")
FINAL_VIDEO_PATH = os.path.join(TEMP_DIR, "final.mp4")

# =========================
# BACKGROUND MUSIC
# =========================

BG_MUSIC_MAP = {
    "None": None,
    "Calm": os.path.join(MUSIC_DIR, "calm.mp3"),
    "Ocean": os.path.join(MUSIC_DIR, "ocean.mp3"),
    "Motivation": os.path.join(MUSIC_DIR, "motivation.mp3"),
}

# =========================
# TEXT / SUBTITLES
# =========================

SCRIPT_TEXT = ""
DISABLE_TEXT_OVERLAY = True
