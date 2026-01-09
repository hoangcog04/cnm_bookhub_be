from fastapi import APIRouter, HTTPException, status
from fastapi.param_functions import Depends
from cnm_bookhub_be.db.dao.ward_dao import WardDAO
from cnm_bookhub_be.db.models.wards import Ward
from cnm_bookhub_be.web.api.wards.schema import WardDTO

router = APIRouter()

# GET Wards with optional province filter and search
@router.get("/", response_model=list[WardDTO])
async def get_wards(
    province_code: str | None = None,
    search: str | None = None,
    dao: WardDAO = Depends(),
) -> list[Ward]:
    return await dao.get_all_wards(province_code=province_code, search=search)