# app/main.py
from fastapi import FastAPI
from youtube_downloader import router as youtube_downloader_router
from audio_video_separator import router as audio_video_separator_router
from transcriber import router as transcribe_media_router
from image_compressor import router as image_compressor_router
# from instagram_downloader import router as instagram_downloader_router 
# from instagram_download_by_date_span import router as instagram_download_by_date_span_router

app = FastAPI()

app.include_router(youtube_downloader_router)
app.include_router(audio_video_separator_router)
app.include_router(transcribe_media_router)
app.include_router(image_compressor_router)
# app.include_router(instagram_downloader_router)
# app.include_router(instagram_download_by_date_span_router)


# the instagram scrapers only kinda work and i have to pip install instaloader into the container for some reason
