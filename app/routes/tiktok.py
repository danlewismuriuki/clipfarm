from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import yt_dlp
import os
import subprocess
from pathlib import Path
import sys

router = APIRouter()

# TEMP_DIR = "temp_videos"
# OUTPUT_DIR = "cleaned_videos"
# WATERMARK_CLI_PATH = "../WatermarkRemover-AI/remwm.py"


TEMP_DIR = "/content/drive/MyDrive/clipfarm/temp_videos"
OUTPUT_DIR = "/content/drive/MyDrive/clipfarm/cleaned_videos"
WATERMARK_CLI_PATH = "/content/drive/MyDrive/WatermarkRemover-AI/remwm.py"

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

class TikTokURL(BaseModel):
    url: str

@router.post("/process_tiktok")
def process_tiktok(video: TikTokURL):
    url = video.url

    if "tiktok.com" not in url:
        raise HTTPException(status_code=400, detail="Only TikTok URLs are supported")
    
    ydl_opts = {
        'outtmpl': os.path.join(TEMP_DIR, '%(id)s.%(ext)s'),
        'format': 'mp4',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloaded_file = ydl.prepare_filename(info)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")
    try:
        output_path = os.path.join(OUTPUT_DIR, Path(downloaded_file).name)
        cmd = [
            sys.executable,
            WATERMARK_CLI_PATH,
            downloaded_file,
            OUTPUT_DIR,
            "--detection-skip", "3"
        ]
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail=f"Watermark CLI not found at {WATERMARK_CLI_PATH}")
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Watermark removal failed: {str(e)}")

    return {
        "original_video": downloaded_file,
        "cleaned_video": output_path
    }
