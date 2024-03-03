from fastapi import APIRouter, BackgroundTasks, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from moviepy.editor import VideoFileClip
from pytube import YouTube
from faster_whisper import WhisperModel
import os
import shutil

router = APIRouter()

TEMP_DIR = "temp_transcriptions"

@router.post("/transcribe_media/", response_class=FileResponse)
async def transcribe_media(background_tasks: BackgroundTasks, youtube_url: str = None, file: UploadFile = File(None)):
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    if youtube_url and file:
        raise HTTPException(status_code=400, detail="Please provide either a YouTube URL or a file, not both.")
    elif youtube_url:
        yt = YouTube(youtube_url)
        video = yt.streams.filter(file_extension='mp4', progressive=True).order_by('resolution').desc().first()
        video_filename = video.default_filename
        video_path = video.download(output_path=TEMP_DIR)
    elif file:
        video_filename = file.filename
        video_path = os.path.join(TEMP_DIR, video_filename)
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    else:
        raise HTTPException(status_code=400, detail="No YouTube URL or file provided.")

    # Extract audio from the video
    clip = VideoFileClip(video_path)
    audio_path = os.path.join(TEMP_DIR, f"{os.path.splitext(video_filename)[0]}_audio.mp3")
    clip.audio.write_audiofile(audio_path)

    # Transcribe the audio
    model = WhisperModel("base.en")
    transcription = " ".join([seg.text for seg in model.transcribe(audio_path)[0]])

    # Save the transcription
    transcript_filename = f"{os.path.splitext(video_filename)[0]}_transcription.txt"
    transcript_file_path = os.path.join(TEMP_DIR, transcript_filename)
    with open(transcript_file_path, "w") as text_file:
        text_file.write(transcription)

    # Instead of scheduling a cleanup here, return the response and suggest scheduling cleanup elsewhere or manually
    # background_tasks.add_task(cleanup_files, TEMP_DIR)

    # Return the transcription file using FileResponse directly without scheduling cleanup in background_tasks
    return FileResponse(path=transcript_file_path, media_type='txt', filename=transcript_filename)

# Keep the cleanup function for manual or scheduled invocation
def cleanup_files(temp_dir: str):
    """Removes the specified directory and its contents."""
    shutil.rmtree(temp_dir, ignore_errors=True)
