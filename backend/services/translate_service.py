import requests
from functools import lru_cache
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TESTING = os.getenv("TESTING") == "1"


@lru_cache(maxsize=100)
def translate(text: str) -> str:

    if TESTING:
        return text

    try:

        logger.info(f"🌍 Перевод текста: {text[:50]}...")

        response = requests.post(
            "https://libretranslate.de/translate",
            json={
                "q": text,
                "source": "ru",
                "target": "en",
                "format": "text"
            },
            timeout=20
        )

        result = response.json()

        translated = result["translatedText"]

        logger.info(f"✅ Переведено: {translated[:50]}...")

        return translated

    except Exception as e:

        logger.error(f"Ошибка перевода: {e}")

        return text