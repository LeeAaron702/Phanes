```
docker build -t leev2/phanes-api .


docker run --name phanes-api -p 4000:91 -v ${PWD}/app:/app leev2/phanes-api uvicorn main:app --host 0.0.0.0 --port 91 --reload


docker push leev2/phanes-api




docker volume create Phanes_volume  

```




Endpoint
POST /download_youtube_video/: Accepts a YouTube URL as input and returns the video file as a downloadable response.
Usage
Send a POST request to the /download_youtube_video/ endpoint with the YouTube URL in the request body.
The server will process the request, download the video to a temporary directory, and return the video file in the response.
After the file is served, a background task will automatically clean up the downloaded file from the server, ensuring efficient use of storage.
Implementation Details
The API is built with FastAPI and uses PyTube to interact with YouTube.
Downloaded videos are stored in a temporary directory named temp_videos.
A background task ensures that after serving the video file to the user, it gets removed from the server.
In case of any errors during the cleanup process, error messages will be logged for troubleshooting.



# Audio/Video Separator Endpoint

The Audio/Video Separator endpoint allows users to download a video from YouTube, separate its audio and video tracks, and then download either the audio or video file.

## Endpoint Description

- **POST** `/separate_audio_video/`: This endpoint accepts a YouTube URL and a return type (audio or video), downloads the video, separates the audio and video tracks, and serves the requested track as a downloadable file.

## Parameters

- `youtube_url` (string): The full URL of the YouTube video you wish to download and separate.
- `return_type` (enum): Select either "audio" or "video" to specify the type of media you want to download. The default is "audio".

## Usage

To use this endpoint:

1. Make a POST request to `/separate_audio_video/` with the YouTube URL and your choice of return type.
2. The server processes the request, separates the audio and video tracks, and provides the requested track as a downloadable file.
3. Click the download link (in Swagger UI or your HTTP client) to download the processed file.

## Implementation Details

- The endpoint leverages `pytube` to download the video from YouTube and `moviepy` to separate the audio and video tracks.
- The temporary files are stored in a directory named `temp_av_files` and are cleaned up after the download completes to ensure efficient use of server storage.
- The API is designed to be interacted with through Swagger UI, making it easy to test and use without additional tooling.

## Getting Started

To interact with the endpoint:

1. Start the FastAPI application and ensure it is running correctly.
2. Access Swagger UI at `http://localhost:4000/docs`.
3. Navigate to the `/separate_audio_video/` endpoint, provide the necessary parameters, and execute the request.
4. Use the response to download the processed media file.

## Notes

- Ensure you adhere to YouTube's terms of service when downloading and processing videos.
- This endpoint is intended for educational or personal use. Always respect copyright and intellectual property rights.



----
# update docker continer
On Your Workstation:
Code Updates: Implement your updates or new features in the FastAPI application.

Rebuild Docker Image: After you've made your changes, rebuild your Docker image:

bash
Copy code
docker build -t leev2/phanes-api .
Tag the Image (Optional): Apply versioning to your Docker image for better management. For example:

bash
Copy code
docker tag leev2/phanes-api leev2/phanes-api:v1.0.1
Push the Image to Docker Hub:

Push the updated image:

bash
Copy code
docker push leev2/phanes-api
If you've applied a version tag:

bash
Copy code
docker push leev2/phanes-api:v1.0.1
On Your Server:
After the image is updated and available on Docker Hub:

Pull the Updated Image: Fetch the latest or specific versioned image:

bash
Copy code
docker pull leev2/phanes-api
Or for a specific version:

bash
Copy code
docker pull leev2/phanes-api:v1.0.1
Stop and Remove the Existing Container: To update the container, you need to stop the current one and remove it:

bash
Copy code
docker stop phanes-api-container
docker rm phanes-api-container
Start the New Container: Launch a new container using the updated image:

bash
Copy code
docker run --name phanes-api-container -p 4000:91 -d leev2/phanes-api
If using a version tag:

bash
Copy code
docker run --name phanes-api-container -p 4000:91 -d leev2/phanes-api:v1.0.1
These steps will guide you through updating the FastAPI application container on your server with the changes made on your workstation, ensuring that your server is always running the latest version of your application.





Stop the Container: First, you stop the Docker container running on your workstation. This ensures that the container's state is preserved, and any changes made within the container are saved.

Tag the Container with a New Version: After stopping the container, you tag it with a new version identifier. This can be a version number or any other identifier that helps you keep track of different versions of your container image. For example, you might tag the container as v1.0.0 for the initial version.

Push the Container to Docker Hub: Once you've tagged the container with the new version, you push the container image to Docker Hub. This makes the updated container image available for deployment on other systems, including your server.

Push Code Changes to GitHub: After pushing the container image to Docker Hub, you push any code changes or updates to your GitHub repository. These code changes represent the changes you've made to your application or service.

CI/CD Pipeline with GitHub Actions: You set up a CI/CD pipeline using GitHub Actions. This pipeline is triggered whenever changes are pushed to your GitHub repository. The pipeline includes steps to build the Docker image, run tests if necessary, and push the updated image to Docker Hub.

Automated Deployment on Server: Once the updated Docker image is pushed to Docker Hub through the CI/CD pipeline, your server pulls the latest version of the Docker image from Docker Hub and deploys it. This ensures that your server always runs the latest version of your application or service.




----
Continuous Integration and Deployment Workflow
This document outlines the steps required to update the code on the server after making changes and pushing them from your workstation to GitHub and Docker Hub.

Workstation Workflow
Development: Write and test your code on your local workstation.

Commit Changes: After completing your changes, commit them to the Git repository on your workstation.

bash
Copy code
git add .
git commit -m "Describe your changes here"
git push origin main
Build and Push Docker Image: Build the Docker image containing your application and push it to Docker Hub.

bash
Copy code
docker build -t leev2/phanes-api .
docker push leev2/phanes-api
Server Workflow
Pull Code Changes from GitHub: SSH into your server and navigate to the directory where your application is deployed.

bash
Copy code
ssh username@your_server_ip
cd /path/to/your/application
Pull the latest changes from your GitHub repository.

bash
Copy code
git pull origin main
Pull Docker Image: Pull the latest Docker image from Docker Hub.

bash
Copy code
docker pull leev2/phanes-api
Stop and Remove Existing Container: If the container is currently running, stop and remove it.

bash
Copy code
docker stop phanes-api
docker rm phanes-api
Run New Container: Start a new container using the updated Docker image, ensuring that it mounts the volume linking to your cloned GitHub repository.

bash
Copy code
docker run --name phanes-api -p 4000:91 -v Phanes_volume:/app leev2/phanes-api uvicorn main:app --host 0.0.0.0 --port 91 --reload
Replace Phanes_volume with the name of your Docker volume.











-----

I gotta make sure the volume is built, then actually build the docker image then run it