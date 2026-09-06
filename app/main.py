import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.database import engine
from app.infrastructure.db.base import Base

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Lifespan startup: Create database tables
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully.")
    except Exception as exc:
        logger.error(
            "Database connection failed during startup (%s: %s). "
            "Server will start, but database operations may fail until connectivity is restored.",
            type(exc).__name__,
            exc,
        )
        
    yield
    # Lifespan shutdown: dispose engine
    await engine.dispose()


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan,
    )

    # Configure CORS
    # NOTE: allow_credentials=True cannot be used with allow_origins=["*"].
    # Browsers reject credentialed requests to wildcard origins (CORS spec violation).
    # To enable credentials (cookies/auth headers), restrict origins to specific domains.
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount API v1 Router
    application.include_router(api_v1_router, prefix=settings.API_V1_STR)

    return application


app = create_application()
