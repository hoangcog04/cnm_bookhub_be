from fastapi import APIRouter, HTTPException, status
from fastapi.param_functions import Depends
from cnm_bookhub_be.db.dao.province_dao import ProvinceDAO
from cnm_bookhub_be.db.models.provinces import Province
from cnm_bookhub_be.web.api.provinces.schema import ProvinceDTO

router = APIRouter()

#GET ALL
@router.get("/", response_model=list[ProvinceDTO])
async def get_provinces(
    limit: int = 10,
    offset: int = 0,
    dao: ProvinceDAO = Depends(),
) -> list[Province]:
    return await dao.get_all_province(limit=limit, offset=offset)
