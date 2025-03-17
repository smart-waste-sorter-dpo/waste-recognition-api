import io
import logging
import numpy as np
import httpx
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError

from src.config import get_settings

settings = get_settings()

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/wastes", tags=["Wastes"])


TF_SERVING_URL = (
    "http://tf_serving:8501/v1/models/trash_classification_model:predict"
)

WASTE_CLASSES = {
    0: "BIODEGRADABLE",
    1: "CARDBOARD",
    2: "GLASS",
    3: "METAL",
    4: "PAPER",
    5: "PLASTIC",
    6: "TRASH",
}


async def predict_image(image: Image.Image) -> tuple[int, float]:
    """Асинхронное предсказание класса отходов через TensorFlow Serving."""
    try:
        # Преобразуем изображение в нужный формат
        image = image.resize((224, 224)).convert("RGB")
        image_array = np.array(image) / 255.0
        image_array = np.expand_dims(
            image_array, axis=0
        ).tolist()  # Преобразуем в список для JSON

        async with httpx.AsyncClient() as client:
            response = await client.post(
                TF_SERVING_URL, json={"instances": image_array}, timeout=5
            )

        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"TensorFlow Serving error: {response.text}",
            )

        prediction = response.json().get("predictions", [None])[0]
        if prediction is None:
            raise ValueError("Invalid response from TensorFlow Serving")

        predicted_class = int(np.argmax(prediction))
        confidence = float(np.max(prediction))

        return predicted_class, confidence

    except (httpx.HTTPError, ValueError, KeyError) as e:
        logger.error(f"Ошибка при предсказании: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input or prediction request failed.",
        )


@router.post(
    "/classify/",
    status_code=status.HTTP_200_OK,
)
async def classify_waste(file: UploadFile = File(...)) -> JSONResponse:
    if file.content_type != "image/jpeg":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Please upload a JPG file.",
        )

    image_bytes = await file.read()

    if len(image_bytes) > settings.MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Image size too large. Please upload an image smaller than {settings.MAX_IMAGE_SIZE / 1024 / 1024}MB.",  # noqa: E501
        )

    try:
        image = Image.open(io.BytesIO(image_bytes))
        print(image.size)

    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File not found.",
        )

    except UnidentifiedImageError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid image file.",
        )

    predicted_class, confidence = await predict_image(image)

    return JSONResponse(
        content={
            "class": WASTE_CLASSES[predicted_class],
            "confidence": float(confidence),
        }
    )
