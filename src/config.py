from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import os

class Settings(BaseSettings):
    # Поддержка DATABASE_URL (для Railway)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # Отдельные параметры (для локальной разработки)
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASS: str = os.getenv("DB_PASS", "postgres")
    DB_NAME: str = os.getenv("DB_NAME", "telegram_bot")
    TOKEN: str = os.getenv("TOKEN", "")

    @property
    def DATABASE_URL_asyncpg(self):
        """Для asyncpg (асинхронный драйвер)"""
        if self.DATABASE_URL:
            # Railway даёт postgresql://, нам нужно postgresql+asyncpg://
            return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def DATABASE_URL_psycopg(self):
        """Для psycopg2 (синхронный драйвер)"""
        if self.DATABASE_URL:
            return self.DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )

# Попытка загрузить настройки
try:
    settings = Settings()
    print("✅ Настройки загружены")
    print(f"📊 Используется DATABASE_URL: {'Да' if settings.DATABASE_URL else 'Нет'}")
    print(f"📊 DB_HOST: {settings.DB_HOST}")
    print(f"📊 DB_NAME: {settings.DB_NAME}")
except Exception as e:
    print(f"❌ Ошибка загрузки настроек: {e}")
    raise