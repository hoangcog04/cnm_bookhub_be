from fastapi.routing import APIRouter

from cnm_bookhub_be.web.api import dummy, echo, monitoring, users
from cnm_bookhub_be.web.api import orders
from cnm_bookhub_be.web.api import order_items
from cnm_bookhub_be.web.api import books

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(users.router)
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(dummy.router, prefix="/dummy", tags=["dummy"])
api_router.include_router(orders.router,prefix="/orders",tags=["orders"])
api_router.include_router(order_items.router,prefix="/order-items",tags=["order-items"])      
api_router.include_router(books.router,prefix="/books",tags=["books"])                


