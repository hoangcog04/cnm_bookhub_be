from fastapi.routing import APIRouter

from cnm_bookhub_be.web.api import (
    categories,
    dummy,
    echo,
    files,
    monitoring,
    users,
)

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(users.router)
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(dummy.router, prefix="/dummy", tags=["dummy"])
api_router.include_router(categories.router, prefix="/category", tags=["category"])
