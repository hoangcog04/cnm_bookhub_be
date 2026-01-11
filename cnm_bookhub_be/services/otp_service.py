import random
import string
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from cnm_bookhub_be.db.models.otp import OTP
from cnm_bookhub_be.services.email_service import email_service, TEMPLATE_OTP_NAME

CODE_LENGTH = 6
OTP_LIFETIME_SECONDS = 300  # 5 minutes

class OTPService:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _generate_code(self) -> str:
        return "".join(random.choices(string.digits, k=CODE_LENGTH))

    async def generate_otp(self, email: str) -> None:
        """
        Generate a new OTP code for the given email, save it to the database,
        and send an email with the code.
        """
        code = self._generate_code()
        
        # Invalidate previous unused OTPs for this email?
        # For simplicity, we just create a new one. The verification checks validity.
        
        otp = OTP(
            email=email,
            otp_code=code,
            expired_at=datetime.utcnow() + timedelta(seconds=OTP_LIFETIME_SECONDS),
            is_used=False
        )
        self.session.add(otp)
        await self.session.commit()

        # Send email
        await email_service.send_email(
            template_name=TEMPLATE_OTP_NAME,
            to_email=email,
            subject="Your OTP Code",
            template_body={"otp_code": code},
        )

    async def verify_otp(self, email: str, code: str) -> bool:
        """
        Verify the OTP code for the given email.
        Mark as used if valid.
        """
        # Find the latest valid OTP for this email
        query = select(OTP).where(
            OTP.email == email,
            OTP.otp_code == code,
            OTP.is_used == False,
            OTP.expired_at > datetime.utcnow()
        ).order_by(OTP.created_at.desc())
        
        result = await self.session.execute(query)
        otp = result.scalars().first()

        if not otp:
            return False

        otp.is_used = True
        await self.session.commit()
        return True
