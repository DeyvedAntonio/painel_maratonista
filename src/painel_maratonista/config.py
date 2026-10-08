"""Configuração centralizada com Pydantic Settings."""

from functools import lru_cache
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "Painel Maratonista"
    app_version: str = "0.2.0"
    debug: bool = Field(default=False, alias="DEBUG")

    # Database
    database_path: Path = Field(default=Path("maratonista.db"), alias="DATABASE_PATH")
    database_echo: bool = Field(default=False, alias="DATABASE_ECHO")

    # TMDb
    tmdb_api_key: Optional[str] = Field(default=None, alias="TMDB_API_KEY")
    tmdb_base_url: str = "https://api.themoviedb.org/3"
    tmdb_image_base: str = "https://image.tmdb.org/t/p/w200"
    tmdb_timeout: int = 10
    tmdb_cache_ttl: int = 3600  # 1 hora

    # Streamlit
    streamlit_port: int = 8501
    streamlit_host: str = "0.0.0.0"
    streamlit_headless: bool = True

    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100

    # Badge thresholds (configuráveis)
    badge_thresholds: dict = Field(default_factory=lambda: {
        "first_steps": 1,
        "marathoner": 10,
        "critic": 5,
        "binge_watcher": 50,
        "film_buff": 20,
        "series_addict": 10,
        "genre_explorer": 5,
        "time_lord": 5000,
        "completionist": 10,
    })


@lru_cache
def get_settings() -> Settings:
    """Retorna instância singleton das configurações."""
    return Settings()


settings = get_settings()