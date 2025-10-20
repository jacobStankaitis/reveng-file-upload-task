from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "file-upload-app"
    API_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    ENV: str = "dev"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    FRONTEND_ORIGIN: str = "http://localhost:3000"
    MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10MB
    CONCURRENT_UPLOAD_LIMIT: int = 100
    REQUEST_TIMEOUT_SEC: int = 30
    ENABLE_METRICS: bool = True
    ENABLE_TLS: bool = False

    FILE_BACKEND: str = "memory"
    FEATURE_REQUIRE_CSRF_HEADER: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
