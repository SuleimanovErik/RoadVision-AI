import requests
import os

CV_SERVICE_URL = "http://192.168.0.125:1488"
API_KEY = os.environ.get("INTERNAL_API_KEY", "")

def analyze_image(image_path):
    with open(image_path, "rb") as f:
        response = requests.post(
            f"{CV_SERVICE_URL}/detect/image",
            files={"file": f},
            headers={"X-API-Key": API_KEY}
        )
    return response.json()

def analyze_video(video_path):
    with open(video_path, "rb") as f:
        response = requests.post(
            f"{CV_SERVICE_URL}/detect/video",
            files={"file": f},
            headers={"X-API-Key": API_KEY}
        )
    return response.json()