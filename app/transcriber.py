from fastapi import APIRouter, BackgroundTasks, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from moviepy.editor import VideoFileClip
from pytube import YouTube
from faster_whisper import WhisperModel
import os
import shutil
import zipfile

router = APIRouter()

TEMP_DIR = "temp_transcriptions"

@router.post("/transcribe_media/", response_class=FileResponse)
async def transcribe_media(background_tasks: BackgroundTasks, youtube_url: str = None, file: UploadFile = File(None)):
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    video_path = None
    source_is_youtube = False

    if youtube_url and file:
        raise HTTPException(status_code=400, detail="Please provide either a YouTube URL or a file, not both.")
    elif youtube_url:
        source_is_youtube = True
        yt = YouTube(youtube_url)
        video = yt.streams.filter(file_extension='mp4', progressive=True).order_by('resolution').desc().first()
        if not video:
            raise HTTPException(status_code=404, detail="No suitable video found.")
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

    # Create a zip file and include the relevant files
    zip_filename = f"{os.path.splitext(video_filename)[0]}_transcription.zip"
    zip_file_path = os.path.join(TEMP_DIR, zip_filename)
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        if source_is_youtube:
            zipf.write(video_path, os.path.basename(video_path))
        zipf.write(audio_path, os.path.basename(audio_path))
        zipf.write(transcript_file_path, os.path.basename(transcript_file_path))

    response = FileResponse(path=zip_file_path, media_type='application/zip', filename=zip_filename)

    # Schedule cleanup task to run after the file is served
    background_tasks.add_task(cleanup_files, TEMP_DIR)

    return response

def cleanup_files(temp_dir: str):
    """Removes the specified directory and its contents."""
    try:
        shutil.rmtree(temp_dir)
    except Exception as e:
        print(f"Error cleaning up transcription files: {e}")
