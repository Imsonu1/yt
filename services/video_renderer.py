import subprocess
from utils.config import VIDEO_PATH, FINAL_VIDEO_PATH, TEMP_DIR, SCRIPT_TEXT

FONT_PATH = "E\\:/yt/assets/fonts/NotoSansDevanagari-Regular.ttf"


def escape_text(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
            .replace(":", "\\:")
            .replace("'", "\\'")
            .replace("%", "\\%")
    )


def render_video(audio_clip):
    duration = audio_clip.duration

    temp_audio = f"{TEMP_DIR}/voice_temp.wav"
    audio_clip = audio_clip.set_fps(44100)
    audio_clip.write_audiofile(temp_audio, verbose=False, logger=None)

    words = SCRIPT_TEXT.strip().split()
    text_filters = []

    if words:
        per_word = max(0.8, duration / len(words))
        t = 0.0

        for word in words:
            start = round(t, 2)
            end = round(t + per_word, 2)

            safe_word = escape_text(word)

            text_filters.append(
                "drawtext="
                f"fontfile={FONT_PATH}:"
                f"text='{safe_word}':"
                "fontsize=96:"
                "fontcolor=yellow:"
                "box=1:"
                "boxcolor=black@0.85:"
                "boxborderw=20:"
                "x=(w-text_w)/2:"
                "y=h*0.15:"
                f"enable='between(t,{start},{end})'"
            )

            t += per_word

    # ✅ ONLY VIDEO TRANSFORMS HERE
    vf_chain = (
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920"
    )

    if text_filters:
        vf_chain += "," + ",".join(text_filters)

    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-i", VIDEO_PATH,
        "-i", temp_audio,
        "-t", str(duration),
        "-vf", vf_chain,
        "-r", "30",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",
        FINAL_VIDEO_PATH
    ]

    subprocess.run(ffmpeg_cmd, check=True)
    return FINAL_VIDEO_PATH
