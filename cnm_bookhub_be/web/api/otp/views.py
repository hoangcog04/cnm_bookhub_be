from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select
from cnm_bookhub_be.db.models.users import User
from cnm_bookhub_be.db.dependencies import get_db_session
from cnm_bookhub_be.services.otp_service import OTPService
from cnm_bookhub_be.web.api.otp.schema import SendOTPRequest, VerifyOTPRequest

router = APIRouter()

@router.post("/send")
async def send_otp(
    payload: SendOTPRequest,
    session: AsyncSession = Depends(get_db_session),
):
    service = OTPService(session)
    await service.generate_otp(payload.email)
    return {"message": "OTP sent successfully"}

@router.post("/verify")
async def verify_otp(
    payload: VerifyOTPRequest,
    session: AsyncSession = Depends(get_db_session),
):
    service = OTPService(session)
    is_valid = await service.verify_otp(payload.email, payload.otp_code)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
    
    return {"message": "OTP verified successfully"}

@router.post("/verify-registration")
async def verify_registration(
    payload: VerifyOTPRequest,
    session: AsyncSession = Depends(get_db_session),
):
    service = OTPService(session)
    is_valid = await service.verify_otp(payload.email, payload.otp_code)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
    
    # Activate user
    query = select(User).where(User.email == payload.email)
    result = await session.execute(query)
    user = result.scalars().first()
    
    if not user:
         raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_verified = True
    await session.commit()

    return {"message": "User verified successfully"}
