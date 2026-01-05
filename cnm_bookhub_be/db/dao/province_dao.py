from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from cnm_bookhub_be.db.dependencies import get_db_session
from cnm_bookhub_be.db.models.provinces import Province

class ProvinceDAO:
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session
        
    #GET ALL
    async def get_all_province(self, limit: int, offset: int) -> list[Province]:
        raw_items = await self.session.execute(
            select(Province).limit(limit).offset(offset),
        )
        return list(raw_items.scalars().fetchall())
        