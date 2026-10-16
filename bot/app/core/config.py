from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str
    GEMINI_API_KEY: str
    DATABASE_URL: str = "postgresql+asyncpg://pepito:pepito_pass@pepito-bot_db_1:5432/pepito_db"
    REDIS_URL: str = "redis://redis:6379/0"
    ADMIN_TELEGRAM_IDS: list[int] = []
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    SUPPORT_URL: str = "https://t.me/pepitopet_support"

    # Web App — public HTTPS URL shown in Telegram WebAppInfo button.
    # Telegram requires HTTPS in production; leave empty to hide the button.
    WEBAPP_PUBLIC_URL: str = ""
    # Internal bind address for the aiohttp HTTP server.
    WEBAPP_BIND_HOST: str = "0.0.0.0"
    WEBAPP_BIND_PORT: int = 8080
    # Bot username (without @) — used to build referral deep-links in the Web App.
    # Set in .env: BOT_USERNAME=pepito_bot
    BOT_USERNAME: str = ""

    SENTRY_DSN: str = ""

    # Optional LLM observability (app/logic/trace.py). Empty = log-only traces.
    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: str = ""
    LANGFUSE_HOST: str = ""

    MOBILE_JWT_SECRET: str = "change_me_in_production"
    MOBILE_JWT_EXPIRE_DAYS: int = 30

    @field_validator("ADMIN_TELEGRAM_IDS", mode="before")
    @classmethod
    def parse_admin_ids(cls, v):
        if isinstance(v, str):
            v = v.strip("[]").replace(" ", "")
            return [int(x) for x in v.split(",") if x]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
