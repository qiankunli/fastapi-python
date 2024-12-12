from fastapi import APIRouter

from app.api.v1.resource import router as resource_router


v1 = APIRouter(prefix="/v1/merlin")
v1.include_router(resource_router)
