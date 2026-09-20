"""Configuracao da aplicacao, carregada a partir do arquivo .env."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuracoes da Daily Artifact API.

    Os valores vem do arquivo .env (veja .env.example). Cada campo possui um
    padrao seguro, de modo que a aplicacao sobe mesmo sem o arquivo presente.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Daily Artifact API"
    app_version: str = "1.0.0"
    database_url: str = "sqlite:///./daily_artifact.db"

    # Mantido como string (e nao list[str]) porque pydantic-settings tentaria
    # interpretar um campo de lista como JSON, o que quebraria com "*".
    cors_origins: str = "*"

    @property
    def cors_origin_list(self) -> list[str]:
        """Converte CORS_ORIGINS em lista, aceitando valores separados por virgula."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Retorna a instancia unica de Settings."""
    return Settings()


settings = get_settings()
