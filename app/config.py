from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SecurePro Website"
    env: str = "development"
    secret_key: str = "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET_KEY"
    access_token_expire_minutes: int = 60
    database_url: str = "sqlite:///./securepro.db"
    allowed_origins: str = "http://localhost:8000,http://127.0.0.1:8000"
    allowed_hosts: str = "localhost,127.0.0.1"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def origins(self) -> list[str]:
        return [item.strip() for item in self.allowed_origins.split(",") if item.strip()]

    @property
    def hosts(self) -> list[str]:
        return [item.strip() for item in self.allowed_hosts.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
