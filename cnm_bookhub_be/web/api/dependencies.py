from cnm_bookhub_be.services.cloudinary_service import CloudinaryService


def get_cloudinary_service() -> CloudinaryService:
    return CloudinaryService()