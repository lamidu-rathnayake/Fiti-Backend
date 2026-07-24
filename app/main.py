from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.database import engine
from app.infrastructure.db.base import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Lifespan startup: Create database tables (ideal for SQLite/dev setups)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
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
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount API v1 Router
    application.include_router(api_v1_router, prefix=settings.API_V1_STR)

    return application


app = create_application()
