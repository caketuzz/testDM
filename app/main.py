from fastapi import FastAPI
from app.api.routes.health import router as health_router
from app.core.Settings import settings
from app.core.Logging import setup_logging


def create_app() -> FastAPI:
    setup_logging(settings.log_level)
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
    )

    app.include_router(health_router)
    return app


app = create_app()
