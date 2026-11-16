# Dockerfile for YouTube Shorts generator demo
# -------------------------------------------------
FROM python:3.12-slim

# 1️⃣ System deps – ffmpeg + OpenGL libraries needed by moviepy
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        libgl1 \
        libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# 2️⃣ Upgrade pip (helps with newer wheels)
RUN pip install --upgrade pip setuptools wheel

# 3️⃣ Set working directory
WORKDIR /app

# 4️⃣ Copy only the requirements first – this caches the layer
COPY requirements.txt .

# 5️⃣ Install Python deps (including moviepy)
RUN pip install --no-cache-dir -r requirements.txt

# 6️⃣ Re‑install moviepy *after* system libs are present
RUN pip install --no-cache-dir moviepy==2.2.1

# 7️⃣ Copy the rest of the source code
COPY . .

# 8️⃣ Expose the port Render will bind to (Render injects $PORT)
EXPOSE 8000

# 9️⃣ Default command – use the $PORT supplied by Render, fallback to 8000
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"]