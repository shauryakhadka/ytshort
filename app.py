import os
import json
from datetime import datetime, date
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from openai import OpenAI
from gtts import gTTS
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
import uuid
import shutil

app = FastAPI()

# Load OpenAI client (API key from env)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Path to usage tracking file (persisted in repo)
USAGE_FILE = "usage.json"
FREE_LIMIT = 2  # free videos per day for non‑premium users

class GenerationRequest(BaseModel):
    prompt: str = Field(..., description="What the short should be about")
    voice: str = Field(default="en", description="Language/voice code for gTTS (e.g., 'en', 'es', 'fr')")
    caption_style: str = Field(default="none", description="Style of captions: 'none', 'simple', 'fancy'")
    premium: bool = Field(default=False, description="Whether the user is a premium subscriber")

def load_usage() -> dict:
    if not os.path.exists(USAGE_FILE):
        return {}
    with open(USAGE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_usage(data: dict):
    with open(USAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def check_quota(premium: bool) -> None:
    today = date.today().isoformat()
    usage = load_usage()
    count = usage.get(today, 0)
    limit = 1000 if premium else FREE_LIMIT
    if count >= limit:
        raise HTTPException(status_code=429, detail="Daily quota exceeded. Upgrade to premium for more videos.")
    usage[today] = count + 1
    save_usage(usage)

def generate_script(prompt: str) -> str:
    # Ask LLM to produce a short script (~30 seconds)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Write a concise spoken script for a 30‑second YouTube Shorts video based on the given prompt. Use simple sentences."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content.strip()

def synthesize_speech(text: str, lang: str) -> str:
    tts = gTTS(text=text, lang=lang)
    audio_path = f"temp_{uuid.uuid4()}.mp3"
    tts.save(audio_path)
    return audio_path

def make_video(audio_path: str, caption_style: str) -> str:
    # Simple background: a plain color image generated on‑the‑fly
    img_path = f"temp_{uuid.uuid4()}.png"
    # Create a single‑color image using moviepy (black background)
    clip = ImageClip(color=(0, 0, 0), size=(720, 1280)).set_duration(5)  # 5 s placeholder
    clip.save_frame(img_path)

    audio = AudioFileClip(audio_path)
    img_clip = ImageClip(img_path).set_duration(audio.duration)
    if caption_style != "none":
        # Add simple text caption on top
        txt = caption_style.upper()
        txt_clip = (img_clip.copy().set_opacity(0).fx(lambda c: c)  # placeholder – real caption would use TextClip
        )
        # Skipping complex caption for brevity
    video = img_clip.set_audio(audio)
    out_path = f"ytshort_{uuid.uuid4()}.mp4"
    video.write_videofile(out_path, codec="libx264", audio_codec="aac", fps=24, verbose=False, logger=None)
    # Cleanup temp files
    os.remove(audio_path)
    os.remove(img_path)
    return out_path

@app.post("/generate")
async def generate(request: GenerationRequest, background: BackgroundTasks):
    # Enforce quota
    check_quota(request.premium)
    # 1. script
    script = generate_script(request.prompt)
    # 2. speech
    audio_path = synthesize_speech(script, request.voice)
    # 3. video
    video_path = make_video(audio_path, request.caption_style)
    # 4. Return path (the server will serve static files from the working dir)
    return {"video_file": video_path, "script": script}

# Serve static files (videos) from the repo root
from fastapi.staticfiles import StaticFiles
app.mount("/videos", StaticFiles(directory="."), name="videos")
