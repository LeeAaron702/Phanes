# image_compressor.py
from typing import List
from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.params import Query
from PIL import Image
import os
import shutil
import zipfile

router = APIRouter()

TEMP_DIR = "temp_images"

quality_mapping = {
    "high": 95,
    "medium": 85,
    "low": 75,
    "very_low": 65,
}

def compress_image(input_path, output_path, quality):
    """Compress an image by adjusting its JPEG quality."""
    image = Image.open(input_path)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    image.save(output_path, format='JPEG', quality=quality, optimize=True)

def is_large_file(file_path, size_threshold):
    """Check if the file exceeds the specified size threshold."""
    file_size = os.path.getsize(file_path) / 1024  # Convert size to kilobytes
    return file_size > size_threshold

@router.post("/bulk_image_compressor/")
async def bulk_image_compressor(
    files: List[UploadFile] = File(...),
    quality: str = Query(default="high", enum=["high", "medium", "low", "very_low"]),
    size_threshold: int = Query(default=500, enum=[500, 750])):

    quality_value = quality_mapping[quality]

    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    saved_files = []
    for file in files:
        file_path = os.path.join(TEMP_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        if is_large_file(file_path, size_threshold):
            saved_files.append(file_path)

    # Compress images that are larger than the threshold
    compressed_files = []
    for file_path in saved_files:
        base, ext = os.path.splitext(file_path)
        compressed_file_path = f"{base}_compressed.jpg"
        compress_image(file_path, compressed_file_path, quality_value)
        compressed_files.append(compressed_file_path)

    # Create a zip file containing the compressed images
    zip_filename = "compressed_images.zip"
    zip_file_path = os.path.join(TEMP_DIR, zip_filename)
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for file_path in compressed_files:
            zipf.write(file_path, os.path.basename(file_path))

    return FileResponse(path=zip_file_path, media_type='application/zip', filename="compressed_images.zip")

