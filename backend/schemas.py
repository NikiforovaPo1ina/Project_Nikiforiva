from pydantic import BaseModel



class TranslateRequest(BaseModel):
    text: str


class TranslateResponse(BaseModel):
    original: str
    translated: str

class GenerationResponse(BaseModel):

    success: bool

    russian_text: str

    english_text: str

    image_path: str

    style_used: str

    generation_time: float

    message: str