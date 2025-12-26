from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from cnm_bookhub_be.db.dependencies import get_db_session
from cnm_bookhub_be.db.models.categories import Category

class CategoryDAO:
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session
        
    #POST
    async def create_category(self, **fields) -> None:
        self.session.add(Category(**fields))
        
    #GET ALL
    async def get_all_category(self, limit: int, offset: int) -> list[Category]:
        raw_items = await self.session.execute(
            select(Category).limit(limit).offset(offset),
        )
        return list(raw_items.scalars().fetchall())

    #GET BY ID
    async def get_category_by_id(self, id: int) -> Category | None:
        result = await self.session.execute(
            select(Category).where(Category.id == id),
        )
        return result.scalar_one_or_none()
    
    #UPDATE
    async def update_category(self, id: int, **fields) -> Category | None:
        item = await self.get_category_by_id(id)
        if iter is None:
            return None
        for key, value in fields.items():
            if value is not None:
                setattr(item, key, value)
                
        await self.session.commit()
        await self.session.refresh(item)
        return item
    
    #DELETE
    async def delete_category(self, id: int) -> bool:
        item = await self.get_category_by_id(id)
        if item is None:
            return False
        
        await self.session.delete(item)
        await self.session.commit()
        return True