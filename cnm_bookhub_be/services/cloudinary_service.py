import asyncio
from typing import Any, Dict, List

import cloudinary
import cloudinary.uploader
from fastapi import UploadFile

from cnm_bookhub_be.settings import settings


class CloudinaryService:
    def __init__(self) -> None:
        cloudinary.config(
            cloud_name=settings.cloud_name,
            api_key=settings.api_key,
            api_secret=settings.api_secret,
        )

    async def upload_images(
        self,
        files: List[UploadFile],
        folder: str = "bookhub",
    ) -> List[Dict[str, str]]:
        tasks = [
            asyncio.to_thread(
                self.upload_image,
                file=file,
                folder=folder,
            )
            for file in files
        ]
        results = await asyncio.gather(*tasks)
        return [
            {"url": result.get("url"), "public_id": result.get("public_id")}
            for result in results
        ]

    def upload_image(self, file: UploadFile, folder: str = "bookhub") -> Dict[str, Any]:
        result = cloudinary.uploader.upload(
            file.file,
            folder=folder,
            resource_type="auto",
        )
        return result

    def delete_image(self, public_id: str) -> Dict[str, Any]:
        result = cloudinary.uploader.destroy(public_id)
        return result