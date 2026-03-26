from fastapi import FastAPI

from app.api.routers.health import router as health_router
from app.api.routers.processing import router as processing_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.include_router(health_router)
    app.include_router(processing_router, prefix="/v1")
    return app


app = create_app()
