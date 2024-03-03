```
docker build -t leev2/phanes-api .


docker run --name phanes-api -p 4000:91 -v ${PWD}/app:/app leev2/phanes-api uvicorn main:app --host 0.0.0.0 --port 91 --reload


docker push leev2/phanes-api

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