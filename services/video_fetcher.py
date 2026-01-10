import requests
from utils.config import BASE_VIDEO_PATH

PIXABAY_API_KEY = "28842671-57a9ca330718ba2018ee9534a"


def fetch_video(keyword):
    url = "https://pixabay.com/api/videos/"
    params = {
        "key": PIXABAY_API_KEY,
        "q": keyword,
        "per_page": 10,
        "safesearch": "true",
        "orientation": "vertical",  # 🔥 IMPORTANT
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    data = response.json()

    if not data.get("hits"):
        raise Exception("No video found for this keyword")

    # -----------------------------
    # Pick best usable video
    # Prefer vertical / large clips
    # -----------------------------
    selected_video_url = None

    for hit in data["hits"]:
        videos = hit.get("videos", {})

        # Prefer large / medium quality
        if "large" in videos:
            selected_video_url = videos["large"]["url"]
            break
        elif "medium" in videos:
            selected_video_url = videos["medium"]["url"]
            break

    if not selected_video_url:
        raise Exception("No suitable video format found")

    # -----------------------------
    # Download video
    # -----------------------------
    with requests.get(selected_video_url, stream=True, timeout=30) as r:
        r.raise_for_status()
        with open(BASE_VIDEO_PATH, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    return BASE_VIDEO_PATH
