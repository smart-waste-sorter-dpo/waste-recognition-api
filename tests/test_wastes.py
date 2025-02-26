import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_wastes_types(client: AsyncClient):
    response = await client.get("/wastes/")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_valid_classify_waste(client: AsyncClient):
    file_path = "tests/assets/waste_img.jpg"

    with open(file_path, "rb") as file:
        files = {"file": ("test_image.jpg", file, "image/jpeg")}

        response = await client.post("/wastes/classify/", files=files)

    assert response.status_code == status.HTTP_200_OK
    assert "class" in response.json()
