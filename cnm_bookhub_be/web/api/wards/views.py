from fastapi import APIRouter, HTTPException, status
from fastapi.param_functions import Depends
from cnm_bookhub_be.db.dao.ward_dao import WardDAO
from cnm_bookhub_be.db.models.wards import Ward
from cnm_bookhub_be.web.api.wards.schema import WardDTO

router = APIRouter()

#GET Wards by province_code
@router.get("/{province_code}", response_model=list[WardDTO])
async def get_wards(
    province_code: str,
    dao: WardDAO = Depends(),
) -> list[Ward]:
    items = await dao.get_ward_by_province_code(province_code)
    if items is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Province not found"
        )
    return items