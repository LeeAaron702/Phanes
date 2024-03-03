from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from moviepy.editor import VideoFileClip
from pytube import YouTube
from enum import Enum
import os
import shutil

class ReturnType(str, Enum):
    audio = "audio"

router = APIRouter()

TEMP_DIR = "temp_av_files"

SUPPORTED_FILE_TYPES = ["mp4", "mov", "avi", "mkv"]

@router.post("/download_extract_audio/")
async def extract_audio(background_tasks: BackgroundTasks, return_type: ReturnType = ReturnType.audio, youtube_url: str = None, file: UploadFile = File(None)):
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    if youtube_url:
        yt = YouTube(youtube_url)
        video = yt.streams.filter(file_extension='mp4', progressive=True).order_by('resolution').desc().first()
        if not video:
            raise HTTPException(status_code=404, detail="No suitable video found.")
        video_path = video.download(output_path=TEMP_DIR)
    elif file:
        if file.filename.split('.')[-1].lower() not in SUPPORTED_FILE_TYPES:
            raise HTTPException(status_code=400, detail=f"Unsupported file type. Supported types: {', '.join(SUPPORTED_FILE_TYPES)}")
        video_path = os.path.join(TEMP_DIR, file.filename)
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    else:
        raise HTTPException(status_code=400, detail="No input source provided.")

    clip = VideoFileClip(video_path)
    
    if return_type == ReturnType.audio:
        audio_path = os.path.join(TEMP_DIR, "audio.mp3")
        clip.audio.write_audiofile(audio_path)
        file_path = audio_path
        media_type = 'audio/mpeg'
        file_name = "audio.mp3"
    else:  # return_type == ReturnType.video, kept for future proofing or extension
        file_path = video_path
        media_type = 'video/mp4'
        file_name = os.path.basename(video_path)

    response = FileResponse(path=file_path, media_type=media_type, filename=file_name)
    
    # Schedule cleanup task to run after file is served
    background_tasks.add_task(cleanup_av_files, TEMP_DIR)

    return response

def cleanup_av_files(temp_dir: str):
    """Removes the specified directory and its contents."""
    try:
        shutil.rmtree(temp_dir)
    except Exception as e:
        print(f"Error cleaning up AV files: {e}")
