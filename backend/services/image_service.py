import requests
import io
import time
from PIL import Image
from backend.config import API_URL, HEADERS
from typing import Optional
import random


def generate_image(
        prompt: str,
        num_steps: int = 4,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None,
        negative_prompt: str = None,
        style: str = "realistic"
) -> Image.Image:
    """Генерация изображения с расширенными параметрами"""

    # Расширяем промпт в зависимости от стиля
    style_keywords = {
        "realistic": "photorealistic, 8K, ultra detailed, sharp focus, professional photography",
        "anime": "anime style, vibrant colors, manga art, cel-shaded, Japanese animation",
        "painting": "oil painting, masterpiece, brush strokes, artistic, framed art",
        "digital": "digital art, concept art, trending on ArtStation, unreal engine, cinematic",
        "fantasy": "fantasy art, magical, epic, mystical, dreamlike, surreal"
    }

    # Добавляем ключевые слова стиля к промпту
    enhanced_prompt = f"{prompt}, {style_keywords.get(style, '')}"

    # Если seed не указан - генерируем случайный каждый раз
    if seed is None:
        seed = random.randint(0, 2 ** 32 - 1)

    parameters = {
        "num_inference_steps": num_steps,
        "guidance_scale": guidance_scale,
        "seed": seed  # Всегда добавляем seed для разнообразия
    }

    if negative_prompt:
        parameters["negative_prompt"] = negative_prompt

    payload = {
        "inputs": enhanced_prompt,
        "parameters": parameters
    }

    print(f"Генерация изображения с параметрами:")
    print(f"  Промпт: {enhanced_prompt[:100]}...")
    print(f"  Стиль: {style}")
    print(f"  Seed: {seed}")
    print(f"  Шаги: {num_steps}")

    retry_count = 0
    max_retries = 3

    while retry_count < max_retries:
        try:
            response = requests.post(
                API_URL,
                headers=HEADERS,
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                print("  Успешно!")
                return Image.open(io.BytesIO(response.content))

            elif response.status_code == 503:
                retry_count += 1
                wait_time = 10 * retry_count
                print(f"  Модель загружается, жду {wait_time} сек...")
                time.sleep(wait_time)

            else:
                error_msg = f"Ошибка API: {response.status_code} - {response.text[:200]}"
                print(f"  {error_msg}")
                raise RuntimeError(error_msg)

        except requests.exceptions.Timeout:
            retry_count += 1
            print(f"  Таймаут, попытка {retry_count}/{max_retries}")
            time.sleep(5)

    raise RuntimeError("Превышено количество попыток генерации")