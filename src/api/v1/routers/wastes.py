import random
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError
import io

from src.config import get_settings


WASTE_CLASSES = {
    0: "BIODEGRADABLE",
    1: "CARDBOARD",
    2: "GLASS",
    3: "METAL",
    4: "PAPER",
    5: "PLASTIC",
    6: "TRASH",
}

settings = get_settings()


router = APIRouter(prefix="/wastes", tags=["Wastes"])


@router.get("/")
async def get_wastes():
    return JSONResponse(content={"classes": list(WASTE_CLASSES.values())})


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

    predicted_class = WASTE_CLASSES[random.randint(0, 6)]

    return JSONResponse(content={"class": predicted_class})
