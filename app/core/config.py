
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str 
    VERSION: str 
    API_V1_STR: str
    
    # Environment
    ENVIRONMENT: str
    DEBUG: bool

    # Database Settings
    DATABASE_URL: str
    

    # Firebase Auth Settings
    MOCK_FIREBASE_AUTH: bool
    FIREBASE_CREDENTIALS_PATH: str | None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
