from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime

from backend.database.db import Base

class Generation(Base):
    __tablename__ = "generations"

    id = Column(Integer, primary_key=True, index=True)

    russian_text = Column(Text)
    english_text = Column(Text)

    image_path = Column(String)

    style_used = Column(String)

    generation_time = Column(Float)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )