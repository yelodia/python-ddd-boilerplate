from functools import lru_cache

from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_env: str = "development"
    app_debug: bool = False
    app_secret_key: str = "dev-secret-key"

    # Storage backend: "json" | "sql" | "ram"
    storage_backend: str = "ram"  # TODO было json, вернуть обратно после тестов

    # JSON storage (Phase 1)
    json_data_dir: str = "data"

    # Database (Phase 2)
    database_url: PostgresDsn | None = None
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # Redis
    redis_url: RedisDsn = "redis://localhost:6379/0"  # type: ignore[assignment]

    # OpenTelemetry
    otel_enabled: bool = False
    otel_service_name: str = "my-app"
    otel_exporter_otlp_endpoint: str = "http://localhost:4317"

    # Logging
    log_level: str = "INFO"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def use_json_storage(self) -> bool:
        return self.storage_backend == "json"


settings = Settings()


@lru_cache
def get_settings() -> Settings:
    return Settings()
