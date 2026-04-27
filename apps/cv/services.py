import requests

CV_SERVICE_URL = "http://192.168.0.111:8080"  # твой микросервис


def analyze_image(image_path):
    with open(image_path, "rb") as f:
        response = requests.post(
            f"{CV_SERVICE_URL}/analyze/image/",
            files={"file": f}
        )

    return response.json()

def analyze_video(video_path):
    with open(video_path, "rb") as f:
        response = requests.post(
            f"{CV_SERVICE_URL}/analyze/video/",
            files={"file": f}
        )

    return response.json()