"""Configurações da aplicação, carregadas de variáveis de ambiente ou do arquivo .env."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NOME: str = "Mapa do Direito"
    APP_VERSAO: str = "1.0.0"
    DEBUG: bool = True

    # SQLite em desenvolvimento. Em produção basta trocar por:
    # postgresql+psycopg://usuario:senha@host:5432/mapa_do_direito
    DATABASE_URL: str = "sqlite:///./mapa_do_direito.db"

    JWT_SECRET: str = "troque-esta-chave-em-producao"
    JWT_ALGORITMO: str = "HS256"
    JWT_EXPIRACAO_MINUTOS: int = 60 * 8

    # Usado para gerar o identificador anônimo da família (nunca armazenamos CPF/NIS).
    SALT_IDENTIFICADOR: str = "salt-local-de-desenvolvimento"


settings = Settings()
