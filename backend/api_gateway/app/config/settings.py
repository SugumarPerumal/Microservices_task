from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    AUTH_SERVICE_URL: str
    USER_SERVICE_URL: str

    INTERNAL_SERVICE_SECRET: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()