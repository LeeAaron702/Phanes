from datetime import date
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
import instaloader
import os
import shutil

router = APIRouter()

INSTAGRAM_DIR = 'instagram_profiles'

@router.get("/download-profile-by-date/{username}")
async def download_instagram_profile_by_date(
    username: str,
    start_date: date = Query(..., description="Start date in the format YYYY-MM-DD"),
    end_date: date = Query(..., description="End date in the format YYYY-MM-DD")
):
    L = instaloader.Instaloader()

    # Check if the base directory exists, if not, create it
    if not os.path.exists(INSTAGRAM_DIR):
        os.makedirs(INSTAGRAM_DIR, exist_ok=True)

    # Define the profile directory and zip file path with date range
    profile_dir = os.path.join(INSTAGRAM_DIR, f"{username}_{start_date.strftime('%Y-%m-%d')}_to_{end_date.strftime('%Y-%m-%d')}")
    os.makedirs(profile_dir, exist_ok=True)

    zip_filepath = os.path.join(INSTAGRAM_DIR, f"{username}_{start_date.strftime('%Y-%m-%d')}_to_{end_date.strftime('%Y-%m-%d')}.zip")

    try:
        current_directory = os.getcwd()
        os.chdir(profile_dir)

        profile = instaloader.Profile.from_username(L.context, username)
        for post in profile.get_posts():
            post_date = post.date_utc.date()  # Adjust post date extraction for comparison
            if start_date <= post_date <= end_date:
                L.download_post(post, target=username)  # Specify the target for organization

        os.chdir(current_directory)  # Return to the original directory before zipping

        shutil.make_archive(zip_filepath.replace('.zip', ''), 'zip', profile_dir)
        return FileResponse(zip_filepath, media_type='application/zip', filename=os.path.basename(zip_filepath))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        shutil.rmtree(profile_dir, ignore_errors=True)  # Clean up the specific directory
