import re
import os


def seconds_to_srt_time(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    ms = int((sec - int(sec)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def generate_srt(script_text, duration, output_path):
    # ✅ CRITICAL FIX: ensure directory exists (Render-safe)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Split by sentence / natural pause
    parts = re.split(r"[।.!?]+", script_text)
    parts = [p.strip() for p in parts if p.strip()]

    if not parts:
        return None

    total_chars = sum(len(p) for p in parts)
    current_time = 0.0

    with open(output_path, "w", encoding="utf-8") as f:
        for idx, line in enumerate(parts, start=1):
            portion = len(line) / total_chars
            block_time = max(0.8, duration * portion)

            start = current_time
            end = min(current_time + block_time, duration)

            f.write(f"{idx}\n")
            f.write(
                f"{seconds_to_srt_time(start)} --> "
                f"{seconds_to_srt_time(end)}\n"
            )
            f.write(line + "\n\n")

            current_time = end

    return output_path
