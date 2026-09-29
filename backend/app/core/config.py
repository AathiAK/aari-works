"""
Application configuration, loaded from environment variables.
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

    # AWS (all optional; unused until Phase 25)
    aws_region: str | None = None
    aws_s3_bucket: str | None = None

    # Checkout pricing: simple flat rules for a single small business.
    shipping_flat_amount: float = 99.00
    free_shipping_threshold: float = 2000.00
    tax_rate_percent: float = 0.0  # set to e.g. 5.0 if GST/tax applies

    # Payments. "mock" runs fully locally with no credentials.
    # NEVER deploy to production with PAYMENT_PROVIDER=mock.
    payment_provider: str = "mock"
    payment_currency: str = "INR"


settings = Settings()
