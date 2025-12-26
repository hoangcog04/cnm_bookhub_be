from fastapi import Depends
from sqlalchemy import select 
from sqlalchemy.ext.asyncio import AsyncSession
from cnm_bookhub_be.db.dependencies import get_db_session
from cnm_bookhub_be.db.models.wards import Ward

class WardDAO:
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session
        
    async def get_ward_by_province_code(self, province_code: str) -> Ward | None:
        result = await self.session.execute(
            select(Ward).where(Ward.province_code == province_code)
        )
        return list(result.scalars().fetchall())