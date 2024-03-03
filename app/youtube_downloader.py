from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import FileResponse
from pytube import YouTube
import os
import shutil

# Initialize an APIRouter instance to create API endpoints
router = APIRouter()

# Define a directory for temporary video storage
TEMP_VIDEO_DIR = "temp_videos"

# Create an API endpoint to download a YouTube video
@router.post("/download_youtube_video/")
async def download_youtube_video(youtube_url: str, background_tasks: BackgroundTasks):
    # If the temporary directory does not exist, create it
    if not os.path.exists(TEMP_VIDEO_DIR):
        os.makedirs(TEMP_VIDEO_DIR)

    # Use PyTube to access the YouTube video
    yt = YouTube(youtube_url)
    # Select the highest resolution MP4 video stream available
    video = yt.streams.filter(file_extension='mp4', progressive=True).order_by('resolution').desc().first()
    
    # Download the selected video stream to the temporary directory
    video_path = video.download(output_path=TEMP_VIDEO_DIR)

    # Create a FileResponse to allow the user to download the video file
    response = FileResponse(path=video_path, media_type='application/octet-stream', filename=video.default_filename)
    
    # Schedule a background task to clean up the video file after the response is sent
    background_tasks.add_task(cleanup_video, video_path)

    return response

def cleanup_video(video_path: str):
    """Function to remove a video file and clean up the directory."""
    try:
        # If the video file exists, remove it
        if os.path.exists(video_path):
            os.remove(video_path)
        # If the temporary directory is empty, remove the directory
        if not os.listdir(TEMP_VIDEO_DIR):
            shutil.rmtree(TEMP_VIDEO_DIR)
    except Exception as e:
        # If any error occurs during cleanup, print the error message
        print(f"Error cleaning up video file: {e}")
