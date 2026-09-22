"""
Application configuration, loaded from environment variables.

Locally, Docker Compose injects these via env_file: .env (added when the
backend service joins docker-compose.yml in Phase 17). When running the
backend standalone (outside Docker), python-dotenv-style loading via
pydantic-settings' env_file picks up backend/.env instead.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Database
    database_url: str

    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    # Image storage
    image_storage: str = "local"
    local_upload_dir: str = "/app/uploads"

    # AWS (all optional — unused until Phase 25, must never be required locally)
    aws_region: str | None = None
    aws_s3_bucket: str | None = None


settings = Settings()
