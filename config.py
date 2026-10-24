from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    database_url: str
    debug: bool = False
    app_env: str = "dev"
    log_level: str = "INFO"
    app_name: str = "Habit Tracker"

@lru_cache
def get_settings() -> Settings:
    return Settings() # type: ignore[call-arg]


settings = get_settings()