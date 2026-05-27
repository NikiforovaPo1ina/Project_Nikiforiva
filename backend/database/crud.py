from sqlalchemy.orm import Session

from backend.database.models_db import Generation

def create_generation(
    db: Session,
    russian_text: str,
    english_text: str,
    image_path: str,
    style_used: str,
    generation_time: float
):
    generation = Generation(
        russian_text=russian_text,
        english_text=english_text,
        image_path=image_path,
        style_used=style_used,
        generation_time=generation_time
    )

    db.add(generation)
    db.commit()
    db.refresh(generation)

    return generation