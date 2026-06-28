from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings

kwargs = {
    "echo": settings.DEBUG,
    "pool_pre_ping": True,
}
if not settings.DATABASE_URL.startswith("sqlite"):
    kwargs["pool_size"] = 20
    kwargs["max_overflow"] = 10

engine = create_async_engine(
    settings.DATABASE_URL,
    **kwargs
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
