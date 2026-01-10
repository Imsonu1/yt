import subprocess


def embed_srt(video_in, srt_in, video_out):
    cmd = [
        "ffmpeg", "-y",
        "-i", video_in,
        "-i", srt_in,
        "-map", "0:v",
        "-map", "0:a?",
        "-map", "1:0",
        "-c:v", "copy",
        "-c:a", "copy",
        "-c:s", "mov_text",
        "-metadata:s:s:0", "language=hin",
        video_out
    ]
    subprocess.run(cmd, check=True)
    return video_out
