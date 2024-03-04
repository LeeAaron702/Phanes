# # Use an official Python runtime as a parent image
# FROM python:3.9-slim

# # Set the working directory in the container to /app
# WORKDIR /app

# # Copy the application code into the container at /app
# COPY ./app /app
# COPY requirements.txt /app/

# # Install any needed packages specified in requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

# # Make port 91 available to the world outside this container
# EXPOSE 91

# # Define the command to run the app
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "91"]



# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the application code into the container at /app
COPY ./app /app
COPY requirements.txt /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 91 available to the world outside this container
EXPOSE 91
