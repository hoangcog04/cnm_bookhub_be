from typing import List, Optional, Tuple
import uuid

from sqlalchemy import delete, select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from cnm_bookhub_be.db.dependencies import get_db_session
from cnm_bookhub_be.db.models.users import User
from cnm_bookhub_be.db.models.wards import Ward
from cnm_bookhub_be.db.models.provinces import Province
from cnm_bookhub_be.db.models.carts import Cart
from cnm_bookhub_be.db.models.orders import Order
from cnm_bookhub_be.db.models.social_accounts import SocialAccount

class UserDAO:
    """Class for accessing user table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get_all_users(
        self,
        limit: int,
        offset: int,
        user_name: Optional[str] = None,
    ) -> Tuple[List[User], int]:
        """
        Get all user models with pagination and filter by name/email.

        :param limit: limit of users.
        :param offset: offset of users.
        :param user_name: filter string for name or email.
        :return: list of users and total pages.
        """
        # Base query
        query = select(User).outerjoin(User.ward).outerjoin(Ward.province)

        if user_name:
            query = query.where(
                or_(
                    User.full_name.ilike(f"%{user_name}%"),
                    User.email.ilike(f"%{user_name}%"),
                )
            )

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_count = await self.session.execute(count_query)
        total = total_count.scalar_one()

        # Execute pagination
        # Note: if offset is passed as page number from FE, we convert to zero-based index or use as needed
        # The frontend seems to send 'offset' as the page number (1, 2, 3...)
        skip = (offset - 1) * limit if offset > 0 else 0
        
        raw_query = query.limit(limit).offset(skip).order_by(User.created_at.desc())
        result = await self.session.execute(raw_query)
        users = list(result.unique().scalars().all())

        total_pages = (total + limit - 1) // limit if limit > 0 else 1

        return users, total_pages

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Get user by id.

        :param user_id: id of user.
        :return: user model or None.
        """
        query = select(User).where(User.id == user_id).outerjoin(User.ward).outerjoin(Ward.province)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def delete_user(self, user_id: uuid.UUID) -> bool:
        """
        Delete a user and all their associated data (Carts, SocialAccounts, Orders).
        
        Note: This is a manual cascade to avoid foreign key constraint issues
        without immediate schema-level ON DELETE CASCADE.
        
        :param user_id: ID of the user to delete.
        :return: True if user was found and deleted, False otherwise.
        """
        # 1. Delete Cart items
        await self.session.execute(delete(Cart).where(Cart.user_id == user_id))
        
        # 2. Delete Social Accounts
        await self.session.execute(delete(SocialAccount).where(SocialAccount.user_id == user_id))
        
        # 3. Handle Orders
        # First delete order items associated with these orders
        from cnm_bookhub_be.db.models.order_items import OrderItem
        order_ids_query = select(Order.id).where(Order.user_id == user_id)
        order_ids_res = await self.session.execute(order_ids_query)
        order_ids = list(order_ids_res.scalars().all())
        
        if order_ids:
            await self.session.execute(delete(OrderItem).where(OrderItem.order_id.in_(order_ids)))
            await self.session.execute(delete(Order).where(Order.id.in_(order_ids)))
        
        # 4. Delete OAuth Accounts (fastapi-users specific if needed, but usually linked)
        # Assuming for now standard users
        
        # 5. Finally delete the user
        result = await self.session.execute(delete(User).where(User.id == user_id))
        
        await self.session.commit()
        return result.rowcount > 0
