from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from fast_zero.settings import Settings

engine = create_async_engine(Settings().DATABASE_URL)


async def get_session():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session


GetSession = Annotated[AsyncSession, Depends(get_session)]
