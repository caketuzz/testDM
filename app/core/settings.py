from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App ---
    app_name: str = "Senior FastAPI Bootstrap"
    version: str = "0.1.0"
    env: str = "dev"
    debug: bool = False
    log_level: str = "INFO"


    # --- Database (future Postgres) ---
    database_url: str | None = None

    # --- Security / secrets ---
    secret_key: str = "CHANGE_ME"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
