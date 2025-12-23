from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import uuid
import time
import os
import random
from datetime import datetime
import json

from backend.services.whisper_service import speech_to_text
from backend.services.translate_service import translate
from backend.services.image_service import generate_image
from backend.models import GenerationRequest, GenerationResponse, GenerationStyle

app = FastAPI(
    title="Voice2Art API",
    description="Преобразование голоса в произведения искусства",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS для Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Папка для результатов
RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)


@app.get("/")
async def root():
    return {
        "message": "Voice2Art API активен",
        "version": "2.0.0",
        "endpoints": {
            "generate": "/generate",
            "history": "/history",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/generate", response_model=GenerationResponse)
async def generate(
        file: UploadFile = File(None),
        style: str = Form("realistic"),
        num_steps: int = Form(4),
        guidance_scale: float = Form(7.5),
        seed: int = Form(None),
        negative_prompt: str = Form(""),
        prompt: str = Form(None)
):
    """Основной эндпоинт для генерации изображений"""
    start_time = time.time()

    try:
        # Логируем полученные параметры
        print("\n" + "=" * 50)
        print("ПАРАМЕТРЫ ЗАПРОСА:")
        print(f"  Файл: {file.filename if file else 'Нет'}")
        print(f"  Стиль: {style}")
        print(f"  Шаги: {num_steps}")
        print(f"  Guidance: {guidance_scale}")
        print(f"  Seed: {seed}")
        print(f"  Negative: {negative_prompt}")
        print(f"  Prompt: {prompt}")
        print("=" * 50)

        # 1. Получение текста
        ru_text = ""

        if file:
            # Аудио режим
            suffix = file.filename.split(".")[-1]
            temp_name = f"temp_{uuid.uuid4()}.{suffix}"

            with open(temp_name, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            ru_text = speech_to_text(temp_name)
            os.remove(temp_name)  # Очистка временного файла

        elif prompt:
            # Текстовый режим
            ru_text = prompt
        else:
            raise HTTPException(status_code=400, detail="Нужно предоставить либо аудио, либо текст")

        # 2. Перевод
        en_text = translate(ru_text)

        # 3. Генерация изображения
        # Если seed не указан - генерируем случайный
        if seed is None:
            seed = random.randint(0, 2 ** 32 - 1)

        print(f"\nГЕНЕРАЦИЯ ИЗОБРАЖЕНИЯ:")
        print(f"  Исходный текст: {ru_text[:100]}...")
        print(f"  Переведенный: {en_text[:100]}...")
        print(f"  Стиль: {style}")
        print(f"  Seed: {seed}")
        print(f"  Шаги: {num_steps}")

        image = generate_image(
            prompt=en_text,
            num_steps=num_steps,
            guidance_scale=guidance_scale,
            seed=seed,
            negative_prompt=negative_prompt,
            style=style
        )

        # 4. Сохранение результата
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = os.path.join(RESULTS_DIR, f"art_{timestamp}_{uuid.uuid4().hex[:8]}.png")
        image.save(image_path)

        generation_time = time.time() - start_time

        return GenerationResponse(
            success=True,
            russian_text=ru_text,
            english_text=en_text,
            image_path=image_path,
            style_used=style,
            generation_time=round(generation_time, 2),
            message=f"Изображение создано в стиле {style}"
        )

    except Exception as e:
        generation_time = time.time() - start_time
        print(f"\nОШИБКА: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка генерации: {str(e)}"
        )


@app.get("/image/{filename}")
async def get_image(filename: str):
    """Получение сгенерированного изображения"""
    image_path = os.path.join(RESULTS_DIR, filename)
    if os.path.exists(image_path):
        return FileResponse(image_path)
    raise HTTPException(status_code=404, detail="Изображение не найдено")


@app.get("/history")
async def get_history(limit: int = 10):
    """Получение истории генераций"""
    images = []
    for file in sorted(os.listdir(RESULTS_DIR), reverse=True)[:limit]:
        if file.endswith(('.png', '.jpg', '.jpeg')):
            images.append({
                "filename": file,
                "path": f"/image/{file}",
                "created": datetime.fromtimestamp(os.path.getctime(os.path.join(RESULTS_DIR, file))).isoformat()
            })
    return {"count": len(images), "images": images}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)