from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import create_api_router
from app.core.config import get_settings
from app.core.exception_handlers import add_exception_handlers
from app.core.logging import configure_logging
from app.schemas.common import ServiceInfoResponse


settings = get_settings()


def create_app() -> FastAPI:
    configure_logging(settings.log_level)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        yield

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        debug=settings.debug,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    add_exception_handlers(app)
    app.include_router(create_api_router(), prefix=settings.api_v1_prefix)

    @app.get("/", include_in_schema=False, response_model=ServiceInfoResponse)
    async def root() -> ServiceInfoResponse:
        return ServiceInfoResponse(
            name=settings.app_name,
            environment=settings.environment,
            version="0.1.0",
            api_prefix=settings.api_v1_prefix,
        )

    return app


app = create_app()
