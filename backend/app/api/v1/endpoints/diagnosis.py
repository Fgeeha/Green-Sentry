from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from app.schemas.diagnosis import DiagnosisResponse, DiagnosisRequest
from app.pipeline.diagnostic_pipeline import DiagnosticPipeline
from app.core.config import settings
import aiofiles
import os
import uuid
from pathlib import Path

router = APIRouter()

# Глобальный экземпляр pipeline
pipeline = DiagnosticPipeline()


@router.post("/", response_model=DiagnosisResponse)
async def diagnose_disease(
        image: UploadFile = File(..., description="Image of the plant"),
        region: str = Form(None),
        climate: str = Form(None),
        plant_age: int = Form(None),
        additional_context: str = Form(None),
        use_reasoning: bool = Form(True)
):
    """
    Диагностика заболевания растения

    - **image**: Фото растения (JPG, PNG)
    - **region**: Регион выращивания
    - **climate**: Климатическая зона
    - **plant_age**: Возраст растения (дни)
    - **additional_context**: Дополнительная информация
    - **use_reasoning**: Использовать reasoning-агент
    """

    # Валидация типа файла
    if image.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only JPG and PNG are allowed."
        )

    # Валидация размера
    contents = await image.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
        )

    # Сохранение файла
    file_id = str(uuid.uuid4())
    file_extension = image.filename.split(".")[-1]
    file_path = Path(settings.UPLOAD_DIR) / f"{file_id}.{file_extension}"

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(contents)

    try:
        # Диагностика
        result = pipeline.diagnose(
            image_path=str(file_path),
            region=region,
            climate=climate,
            plant_age=plant_age,
            additional_context=additional_context,
            use_reasoning=use_reasoning
        )

        return JSONResponse(content=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Удаление временного файла
        if file_path.exists():
            os.unlink(file_path)


@router.get("/diseases")
async def get_diseases():
    """Получить список поддерживаемых заболеваний"""
    from app.models.cv_model import PlantDiseaseClassifier

    return {
        "diseases": [
            {
                "id": disease,
                "name_ru": PlantDiseaseClassifier.DISEASE_NAMES_RU[disease]
            }
            for disease in PlantDiseaseClassifier.DISEASE_CLASSES
        ]
    }