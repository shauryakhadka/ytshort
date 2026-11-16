# Dockerfile for YouTube Shorts generator demo
# -------------------------------------------------
# Base image with Python and ffmpeg (required by moviepy)
FROM python:3.12-slim

# Install ffmpeg (moviepy dependency)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy only the requirements first to leverage Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the source code
COPY . .

# Expose the port the FastAPI server will run on
EXPOSE 8000

# Command to start the API
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
