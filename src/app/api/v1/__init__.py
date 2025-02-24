from fastapi import APIRouter
from . import routers as routers


router = APIRouter(prefix="/v1")

router.include_router(routers.wastes)
