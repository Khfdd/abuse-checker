from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path


class Settings(BaseSettings):
    PROXY: str | None = Field(init=False, default=None)
    SLEEP: int = 1800
    DATA_DIR: Path = Path("data")

    REMNAWAVE_API_BASE_URL: str = Field(init=False)
    REMNAWAVE_API_TOKEN: str = Field(init=False)
    REMNAWAVE_BLOCK_SQUAD: str = Field(init=False)

    MAXMIND_ACCOUNT_ID: str = Field(init=False)
    MAXMIND_LICENSE_KEY: str = Field(init=False)

    TELEGRAM_BOT_TOKEN: str = Field(init=False)
    TELEGRAM_CHAT_ID: int = Field(init=False)
    TELEGRAM_TOPIC_ID: int = Field(init=False)

    debug: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
