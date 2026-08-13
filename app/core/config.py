from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    PROJECT_NAME: str = "Fiti — Smart Tailoring Platform API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database Settings
    DATABASE_URL: str = Field(validation_alias="CONNECTION_STRING")

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def use_async_postgres_driver(cls, value: str) -> str:
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        return value

    # Firebase Auth Settings
    # IMPORTANT: Default is False — set MOCK_FIREBASE_AUTH=true in .env for local dev only.
    # Never set this to True in production — all endpoints will bypass auth checks.
    MOCK_FIREBASE_AUTH: bool = False
    FIREBASE_CREDENTIALS_PATH: str | None = None

    # Admin Backend — used by GET /auth/me/role to redirect admin users
    # In Phase 1 (shared frontend), admin redirects to an internal route.
    # Change to full URL (e.g. https://admin.fiti.com) when admin frontend is separated.
    ADMIN_BACKEND_URL: str = ""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
