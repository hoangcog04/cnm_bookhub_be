from typing import List, Optional, Tuple
from fastapi import Depends
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from cnm_bookhub_be.db.dependencies import get_db_session
from cnm_bookhub_be.db.models.categories import Category

class CategoryDAO:
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session
        
    #POST
    async def create_category(self, **fields) -> Category:
        category = Category(**fields)
        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category)
        return category
        
    #GET ALL
    async def get_all_category(
        self, 
        limit: int, 
        offset: int,
        name: Optional[str] = None
    ) -> Tuple[List[Category], int]:
        query = select(Category).options(selectinload(Category.books))
        
        if name:
            query = query.where(Category.name.ilike(f"%{name}%"))
            
        # Count total
        count_query = select(func.count(Category.id))
        if name:
            count_query = count_query.where(Category.name.ilike(f"%{name}%"))
            
        total_count = await self.session.execute(count_query)
        total = total_count.scalar_one()

        # Pagination logic (offset 1-based from FE)
        skip = (offset - 1) * limit if offset > 0 else 0
        
        raw_items = await self.session.execute(
            query.limit(limit).offset(skip),
        )
        items = list(raw_items.scalars().unique().all())
        
        total_pages = (total + limit - 1) // limit if limit > 0 else 1
        
        return items, total_pages

    #GET BY ID
    async def get_category_by_id(self, id: int) -> Category | None:
        result = await self.session.execute(
            select(Category).options(selectinload(Category.books)).where(Category.id == id),
        )
        return result.scalar_one_or_none()
    
    #UPDATE
    async def update_category(self, id: int, **fields) -> Category | None:
        item = await self.get_category_by_id(id)
        if item is None:
            return None
            
        for key, value in fields.items():
            if value is not None and hasattr(item, key):
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