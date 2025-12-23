import os
from transformers import pipeline
from pathlib import Path

# --- Принудительно указываем путь к ffmpeg ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent
FFMPEG_PATH = BASE_DIR / "ffmpeg" / "bin"

os.environ["PATH"] += os.pathsep + str(FFMPEG_PATH)

print("🎙Loading Whisper...")
whisper = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-tiny"
)

def speech_to_text(audio_path: str) -> str:
    result = whisper(audio_path)
    return result["text"]


