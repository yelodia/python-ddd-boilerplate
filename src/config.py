from functools import lru_cache

from pydantic import PostgresDsn, RedisDsn, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# TODO для чувствительных параметров (например, API-ключей и паролей) стоит использовать специальные типы,
#  (например, SecretStr вместо обычных строк str), чтобы избежать их утечки в логи или отладочные traceback'и:
#  https://pydantic.dev/docs/validation/latest/api/pydantic/types/#pydantic.types.SecretStr


# константы-литералы для удобства & избегания "магических строк" в коде
SQL = 'sql'
JSON = 'json'
RAM = 'ram'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),  # "искать .env в текущей и в родительской папке"
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_env: str = "development"
    app_debug: bool = False
    app_secret_key: str = "dev-secret-key"

    # Storage backend: SQL | JSON | RAM
    storage_backend: str = JSON

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

    @model_validator(mode="before")
    @classmethod
    def lowercase_fields(cls, values: dict) -> dict:
        """
        Приведение специфичных полей к ожидаемому формату (регистру).

        Да, благодаря pydantic_settings и его настройке case_sensitive=False,
        поля будут не чувствительны к регистру при считывании из .env или из переменных окружения (ENV),
        однако в сам Settings() они будут записаны ровно в том виде, в котором были объявлены в .env или ENV.

        Этот валидатор гарантирует, что даже если в .env будет указано "SQL", "Sql" или "sql",
        то внутри приложения мы всегда будем работать со значениями в ожидаемом регистре: "sql".
        """
        # for fields to lowercase
        for key in ("app_env", "storage_backend"):
            if isinstance(values.get(key), str):
                values[key] = values[key].lower()

        # for fields to uppercase
        for key in ("log_level",):
            if isinstance(values.get(key), str):
                values[key] = values[key].upper()

        return values


settings = Settings()


@lru_cache
def get_settings() -> Settings:
    return Settings()
