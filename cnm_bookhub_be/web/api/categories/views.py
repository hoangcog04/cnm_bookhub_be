from fastapi import APIRouter, HTTPException, status
from fastapi.param_functions import Depends
from cnm_bookhub_be.db.dao.category_dao import CategoryDAO
from cnm_bookhub_be.db.models.categories import Category
from cnm_bookhub_be.web.api.categories.schema import (
    CategoryDTO, 
    CategoryInputDTO, 
    CategoryUpdateDTO,
)

router = APIRouter()

#GET ALL
@router.get("/", response_model=list[CategoryDTO])
async def get_categories(
    limit: int = 10, 
    offset: int = 0, 
    dao: CategoryDAO = Depends(),
) -> list[Category]:
    return await dao.get_all_category(limit=limit, offset=offset)

#GET BY ID
@router.get("/{id}", response_model=CategoryDTO)
async def get_category(
    id: int,
    dao: CategoryDAO = Depends(),
) -> Category:
    item = await dao.get_category_by_id(id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found",)
    return item
    
#POST
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_category(
    new_item: CategoryInputDTO,
    dao: CategoryDAO = Depends(),
) -> None:
    await dao.create_category(**new_item.model_dump())
    
#PUT
@router.put("/{id}", response_model=CategoryDTO)
async def update_category(
    id: int,
    update_data: CategoryUpdateDTO,
    dao: CategoryDAO = Depends(),
) -> Category:
    item = await dao.update_category(id=id, **update_data.model_dump(exclude_none=True))
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return item

#DELETE
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    id: int,
    dao: CategoryDAO = Depends(),
) -> None:
    success = await dao.delete_category(id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

