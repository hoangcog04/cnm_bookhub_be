import asyncio
from typing import List

from fastapi import APIRouter, File, UploadFile
from fastapi.param_functions import Depends

from cnm_bookhub_be.services.cloudinary_service import CloudinaryService
from cnm_bookhub_be.web.api.dependencies import get_cloudinary_service

router = APIRouter()


@router.post("/upload_multiple")
async def upload_files(
    files: List[UploadFile] = File(...),
    cloudinary_service: CloudinaryService = Depends(get_cloudinary_service),
) -> dict[str, List[dict[str, str]]]:
    results = await cloudinary_service.upload_images(files=files, folder="uploads")
    return {"files": results}


@router.post("/upload_single")
async def upload_single_file(
    file: UploadFile = File(...),
    cloudinary_service: CloudinaryService = Depends(get_cloudinary_service),
) -> dict[str, str]:
    result = await asyncio.to_thread(
        cloudinary_service.upload_image,
        file=file,
        folder="uploads",
    )
    return {"url": result.get("url"), "public_id": result.get("public_id")}

@router.delete("/delete/{public_id:path}")
async def delete_file(
    public_id: str,
    cloudinary_service: CloudinaryService = Depends(get_cloudinary_service),
) -> dict[str, str]:
    result = await asyncio.to_thread(cloudinary_service.delete_image, public_id)
    return {"result": result.get("result", "error"), "public_id": public_id}