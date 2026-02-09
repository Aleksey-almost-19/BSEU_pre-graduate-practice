import asyncio
from typing import Annotated

from sqlalchemy import String, create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from config import settings

sync_engine = create_engine(
    url=settings.DATABASE_URL_psycopg,
    echo=True,
    # pool_size=5,
    # max_overflow=10,
)

async_engine = create_async_engine(
    url=settings.DATABASE_URL_asyncpg,
    echo=True,
)

session_factory = sessionmaker(sync_engine)
async_session_factory = async_sessionmaker(async_engine)

str_256 = Annotated[str, 256]

class Base(DeclarativeBase):
    type_annotation_map = {
        str_256: String(256)
    }

    repr_cols_num = 3
    repr_cols = tuple()
    
    def __repr__(self):
        """Relationships не используются в repr(), т.к. могут вести к неожиданным подгрузкам"""
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"
    
    if __name__ == "__main__":
        print("=" * 50)
        print("DATABASE CONNECTION TEST")
        print("=" * 50)
    
    # Тест синхронного подключения
        print("\n1. Testing SYNC connection (psycopg2)...")
        try:
            with sync_engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))  # Добавьте text()
                version = result.scalar()
                print(f"   ✅ PostgreSQL version: {version}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Тест асинхронного подключения
        print("\n2. Testing ASYNC connection (asyncpg)...")
    
        async def test_async():
            try:
                async with async_engine.connect() as conn:
                    result = await conn.execute(text("SELECT 1 as test"))  # Добавьте text()
                    row = result.first()
                    print(f"   ✅ Async test query result: {row.test}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    # Запускаем асинхронный тест
        asyncio.run(test_async())
    
        print("\n" + "=" * 50)
        print("ALL TESTS COMPLETED")
        print("=" * 50)