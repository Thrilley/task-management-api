from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Defaults make unit tests importable without a local .env file.
    # Docker overrides them through its environment file.
    database_url: str = "postgresql+asyncpg://task_manager:local-dev-only@localhost:5432/task_manager"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "local-development-secret-change-before-production"
    jwt_expire_minutes: int = 30


settings = Settings()
