from fastapi import APIRouter

from cnm_bookhub_be.services.email_service import (
    TEMPLATE_LINK_VERIFICATION_NAME,
    TEMPLATE_OTP_NAME,
    email_service,
)

router = APIRouter()


@router.post("/send-mail-otp")
async def api_send_mail_otp() -> dict[str, bool]:
    result = await email_service.send_email(
        template_name=TEMPLATE_OTP_NAME,
        to_email="devto@localhost.com",
        subject="Hello World",
        template_body={"username": "Hoang", "otp_code": "123456", "expires_in": "10"},
    )
    return {"result": result}


@router.post("/send-mail-link-verification")
async def api_send_mail_link_verification() -> dict[str, bool]:
    result = await email_service.send_email(
        template_name=TEMPLATE_LINK_VERIFICATION_NAME,
        to_email="devto@localhost.com",
        subject="Hello World",
        template_body={
            "username": "Hoang",
            "verify_url": "https://www.google.com",
        },
    )
    return {"result": result}
