from fastapi import Depends
from sqlalchemy import select 
from sqlalchemy.ext.asyncio import AsyncSession
from cnm_bookhub_be.db.dependencies import get_db_session
from cnm_bookhub_be.db.models.wards import Ward

class WardDAO:
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session
        
    async def get_all_wards(
        self, 
        province_code: str | None = None, 
        search: str | None = None
    ) -> list[Ward]:
        query = select(Ward)
        
        if province_code:
            query = query.where(Ward.province_code == province_code)
        
        if search:
            query = query.where(Ward.full_name.ilike(f"%{search}%"))
        
        result = await self.session.execute(query)
        return list(result.scalars().fetchall())