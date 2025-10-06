from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = (
        "mssql+pyodbc://sa:YourStrong!Passw0rd@mssql:1433/clubdb?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
    )
    jwt_secret: str = "devsecretchangeme"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 8

    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: str = "noreply@example.com"

    class Config:
        env_prefix = ""
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()