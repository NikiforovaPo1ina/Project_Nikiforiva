from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class GenerationStyle(str, Enum):
    REALISTIC = "realistic"
    ANIME = "anime"
    PAINTING = "painting"
    DIGITAL = "digital"
    FANTASY = "fantasy"

class GenerationRequest(BaseModel):
    prompt: Optional[str] = None
    audio_file: Optional[str] = None
    style: GenerationStyle = GenerationStyle.REALISTIC
    num_steps: int = Field(4, ge=1, le=10)
    guidance_scale: float = Field(7.5, ge=1.0, le=20.0)
    seed: Optional[int] = None
    negative_prompt: str = ""

class GenerationResponse(BaseModel):
    success: bool
    russian_text: str
    english_text: str
    image_path: str
    style_used: str
    generation_time: float
    message: str = ""