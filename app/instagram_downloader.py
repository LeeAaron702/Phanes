from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import instaloader
import shutil
import os

router = APIRouter()

# Define the base directory for Instagram profiles
INSTAGRAM_DIR = 'instagram_profiles'

@router.get("/download-profile/{username}")
async def download_instagram_profile(username: str):
    # Create an instance of Instaloader
    L = instaloader.Instaloader()

    # Ensure the base directory exists
    if not os.path.exists(INSTAGRAM_DIR):
        os.makedirs(INSTAGRAM_DIR, exist_ok=True)

    # Define the directory where we want to save the profile's data
    profile_dir = os.path.join(INSTAGRAM_DIR, username)

    # Create the profile directory
    os.makedirs(profile_dir, exist_ok=True)

    # Define the path to the zip file that will be created
    zip_filepath = os.path.join(INSTAGRAM_DIR, f"{username}.zip")

    try:
        # Set the current working directory to the profile directory
        current_directory = os.getcwd()
        os.chdir(profile_dir)

        # Download the profile's posts
        profile = instaloader.Profile.from_username(L.context, username)
        for post in profile.get_posts():
            L.download_post(post, target=username)

        # Return to the original directory
        os.chdir(current_directory)

        # Create the zip archive
        shutil.make_archive(zip_filepath.replace('.zip', ''), 'zip', profile_dir)

        # Return the zip file as a downloadable response
        return FileResponse(zip_filepath, media_type='application/zip', filename=f"{username}.zip")

    except Exception as e:
        # If anything goes wrong, raise an HTTP exception with the details
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up by removing the profile directory after zipping
        shutil.rmtree(profile_dir, ignore_errors=True)
