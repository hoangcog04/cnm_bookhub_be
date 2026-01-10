from fastapi import APIRouter, HTTPException, status
from fastapi.param_functions import Depends

from cnm_bookhub_be.db.dao.province_dao import ProvinceDAO
from cnm_bookhub_be.db.models.provinces import Province
from cnm_bookhub_be.web.api.provinces.schema import ProvinceDTO

router = APIRouter()


# GET ALL with optional search
@router.get("/", response_model=list[ProvinceDTO])
async def get_provinces(
    search: str | None = None,
    dao: ProvinceDAO = Depends(),
) -> list[Province]:
    return await dao.get_all_province(search=search)
