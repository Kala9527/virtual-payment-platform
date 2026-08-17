from functools import lru_cache
from pathlib import Path

from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_DIR = BACKEND_DIR.parent
APP_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    app_name: str = "Virtual Payment Platform"
    app_env: str = "local"
    api_prefix: str = "/api"
    frontend_origin: str = "http://localhost:5176"
    frontend_origins: str = "http://localhost:5176,http://127.0.0.1:5176"
    database_url: str = f"sqlite:///{(BACKEND_DIR / 'app.db').as_posix()}"

    merchant_email: EmailStr = "merchant@example.com"
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_email: EmailStr = "no-reply@example.com"
    smtp_use_tls: bool = True

    assets_dir: Path = APP_DIR / "assets"
    frontend_dist_dir: Path = PROJECT_DIR / "frontend" / "dist"
    outbox_dir: Path = BACKEND_DIR / "outbox"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.assets_dir.mkdir(parents=True, exist_ok=True)
    settings.outbox_dir.mkdir(parents=True, exist_ok=True)
    return settings
