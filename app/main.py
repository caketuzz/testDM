from fastapi import FastAPI
from app.api.routes.health import router as health_router
from app.api.routes.registration import router as registration_router
from app.core.settings import settings
from app.core.logging import setup_logging
from app.core.lifespan import lifespan


def create_app() -> FastAPI:
    setup_logging(settings.log_level)
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        lifespan=lifespan,
    )

    app.include_router(health_router)
    app.include_router(registration_router)
    return app


app = create_app()
