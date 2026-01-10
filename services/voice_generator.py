import time
from gtts import gTTS
from utils.config import TEMP_AUDIO_PATH


def generate_ai_voice(text, lang="hi"):
    """
    Safe gTTS wrapper for Streamlit
    """
    if not text.strip():
        raise ValueError("Empty text for TTS")

    # Retry logic (VERY important)
    last_error = None
    for attempt in range(3):
        try:
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(TEMP_AUDIO_PATH)
            return TEMP_AUDIO_PATH
        except Exception as e:
            last_error = e
            time.sleep(1)  # give network time

    # If all retries fail
    raise RuntimeError(f"gTTS failed after retries: {last_error}")
