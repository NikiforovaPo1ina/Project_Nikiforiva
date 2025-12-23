from transformers import pipeline
from functools import lru_cache
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("Загрузка переводчика...")
translator = pipeline(
    "translation_ru_to_en",
    model="Helsinki-NLP/opus-mt-ru-en",
    device=-1  # CPU для стабильности
)

@lru_cache(maxsize=100)
def translate(text: str) -> str:
    """Перевод с кэшированием частых запросов"""
    try:
        logger.info(f"Перевод текста: {text[:50]}...")
        result = translator(text)[0]["translation_text"]
        logger.info(f"Переведено как: {result[:50]}...")
        return result
    except Exception as e:
        logger.error(f"Ошибка перевода: {e}")
        return text  # Возвращаем оригинал при ошибке