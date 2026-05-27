from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from functools import lru_cache
import logging
import os
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

model = None
tokenizer = None

# Режим для прогона тестов
TESTING = os.getenv("TESTING") == "1"

def load_translator():

    global model, tokenizer

    # Если включен тестовый режим - выход
    if TESTING:
        return

    if model is None or tokenizer is None:


        logger.info("🌍 Загрузка переводчика...")

        model_name = "Helsinki-NLP/opus-mt-ru-en"

        tokenizer = AutoTokenizer.from_pretrained(model_name)

        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

        logger.info("✅ Переводчик загружен")


@lru_cache(maxsize=100)
def translate(text: str) -> str:

    # Во время тестов просто возвращаем текст
    if TESTING:
        return text
    try:

        load_translator()

        logger.info(f"Перевод текста: {text[:50]}...")

        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )

        outputs = model.generate(
            **inputs,
            max_length=512
        )

        result = tokenizer.decode(
            outputs[0],
            skip_special_tokens=True
        )

        logger.info(f"Переведено как: {result[:50]}...")

        return result

    except Exception as e:

        logger.error(f"Ошибка перевода: {e}")

        return text