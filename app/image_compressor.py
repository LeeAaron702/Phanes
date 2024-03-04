from fastapi import APIRouter, File, UploadFile, Query, BackgroundTasks
from starlette.responses import FileResponse
from PIL import Image
import os
import shutil
import zipfile
from typing import List

router = APIRouter()

TEMP_DIR = "temp_images"
EXTRACTED_DIR = "extracted_images"

quality_mapping = {
    "high": 80,
    "medium": 75,
    "low": 60,
    "very low": 50,
}

SUPPORTED_IMAGE_FORMATS = ['jpg', 'jpeg', 'png']

def compress_image(input_path, output_path, quality):
    """Compress an image by adjusting its JPEG quality."""
    with Image.open(input_path) as image:
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image.save(output_path, format='JPEG', quality=quality, optimize=True)

def is_large_file(file_path, size_threshold):
    """Check if the file size exceeds the specified threshold."""
    file_size = os.path.getsize(file_path) / 1024  # Convert to kilobytes
    return file_size > size_threshold

def process_single_image(file_path, quality_value, size_threshold):
    """Process a single image file."""
    if is_large_file(file_path, size_threshold):
        base, ext = os.path.splitext(file_path)
        optimized_file_path = f"{base}_optimize_{quality_value}{ext}"
        compress_image(file_path, optimized_file_path, quality_mapping[quality_value])
        return optimized_file_path
    return file_path

def process_image_files(directory, quality_value, size_threshold):
    """Process, compress if necessary, and collect image files from the given directory."""
    processed_files = []
    for root, _, files in os.walk(directory):
        for filename in files:
            if not filename.lower().endswith(tuple(SUPPORTED_IMAGE_FORMATS)):
                continue  # Skip unsupported file formats

            file_path = os.path.join(root, filename)
            processed_file_path = process_single_image(file_path, quality_value, size_threshold)
            processed_files.append((processed_file_path, os.path.relpath(processed_file_path, directory)))
    return processed_files

def cleanup_dirs(dirs: List[str]):
    """Removes specified directories and their contents."""
    for dir_path in dirs:
        shutil.rmtree(dir_path, ignore_errors=True)

@router.post("/bulk_image_compressor/")
async def bulk_image_compressor(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    quality: str = Query(default="high", enum=["high", "medium", "low", "very low"]),
    size_threshold: int = Query(default=500, enum=[500, 750])):
    
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
    if not os.path.exists(EXTRACTED_DIR):
        os.makedirs(EXTRACTED_DIR)

    cleanup_paths = []

    for file in files:
        file_path = os.path.join(TEMP_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        if file.filename.lower().endswith('.zip'):
            # Handle ZIP file upload
            original_zip_filename, _ = os.path.splitext(file.filename)
            extraction_path = os.path.join(EXTRACTED_DIR, original_zip_filename)
            os.makedirs(extraction_path, exist_ok=True)
            cleanup_paths.append(extraction_path)
            zip_ref = zipfile.ZipFile(file_path, 'r')
            zip_ref.extractall(extraction_path)
            zip_ref.close()

            processed_files = process_image_files(extraction_path, quality, size_threshold)

            compressed_zip_filename = f"{original_zip_filename}_compressed_{quality}.zip"
            compressed_zip_file_path = os.path.join(TEMP_DIR, compressed_zip_filename)

            with zipfile.ZipFile(compressed_zip_file_path, 'w') as zipf:
                for file_path, arcname in processed_files:
                    zipf.write(file_path, arcname)

        else:
            # Handle single image file upload
            optimized_file_path = process_single_image(file_path, quality, size_threshold)
            compressed_zip_filename = f"{os.path.splitext(file.filename)[0]}_compressed_{quality}.zip"
            compressed_zip_file_path = os.path.join(TEMP_DIR, compressed_zip_filename)

            with zipfile.ZipFile(compressed_zip_file_path, 'w') as zipf:
                arcname = os.path.basename(optimized_file_path)
                zipf.write(optimized_file_path, arcname)

    # Schedule cleanup task to remove temporary directories after response is sent
    cleanup_paths.append(TEMP_DIR)
    background_tasks.add_task(cleanup_dirs, cleanup_paths)

    return FileResponse(path=compressed_zip_file_path, media_type='application/zip', filename=compressed_zip_filename)
