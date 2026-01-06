from abc import ABC, abstractmethod
from http import HTTPStatus
from pathlib import Path
from typing import Any

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import NameEmail, SecretStr
from sendgrid import ClickTracking, SendGridAPIClient, TrackingSettings
from sendgrid.helpers.mail import Mail

from cnm_bookhub_be.settings import settings

TEMPLATE_OTP_NAME = "OTP_MAIL"
TEMPLATE_LINK_VERIFICATION_NAME = "LINK_VERIFICATION_MAIL"
_mailpit_templates = {
    TEMPLATE_OTP_NAME: "otp_mail.html",
    TEMPLATE_LINK_VERIFICATION_NAME: "link_verification_mail.html",
}
_sendgrid_templates = {
    TEMPLATE_OTP_NAME: "d-7a9e94e48a304cbdaccbf6053c988c3f",
    TEMPLATE_LINK_VERIFICATION_NAME: "d-29030853d30f4c6486ca255508583083",
}


class EmailService(ABC):
    @abstractmethod
    async def send_email(
        self,
        *,
        template_name: str,
        to_email: str,
        subject: str,
        template_body: dict[str, Any] | None = None,
    ) -> bool:
        pass


class MailpitService(EmailService):
    def __init__(self) -> None:
        self.conf = ConnectionConfig(
            MAIL_USERNAME="",
            MAIL_PASSWORD=SecretStr(""),
            MAIL_FROM="devfrom@localhost.com",
            MAIL_FROM_NAME="DevFromName",
            MAIL_PORT=settings.mailpit_port,
            MAIL_SERVER=settings.mailpit_host,
            MAIL_STARTTLS=False,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=False,
            TEMPLATE_FOLDER=Path(__file__).parent / "templates",
        )
        self.fm = FastMail(self.conf)

    async def send_email(
        self,
        *,
        template_name: str,
        to_email: str,
        subject: str,
        template_body: dict[str, Any] | None = None,
    ) -> bool:
        template_path = _mailpit_templates[template_name]
        message = MessageSchema(
            subject=subject,
            recipients=[NameEmail(name="DevTo", email=to_email)],
            template_body=template_body,
            subtype=MessageType.html,
        )
        await self.fm.send_message(message, template_name=template_path)

        return True


class SendGridService(EmailService):
    def __init__(self) -> None:
        self.client = SendGridAPIClient(settings.sendgrid_api_key)
        self.from_email = settings.sendgrid_from_email
        self.tracking_settings = TrackingSettings(
            click_tracking=ClickTracking(enable=False, enable_text=False)
        )

    async def send_email(
        self,
        *,
        template_name: str,
        to_email: str,
        subject: str,
        template_body: dict[str, Any],
    ) -> bool:
        message = Mail(
            from_email=(self.from_email),
            to_emails=to_email,
            subject=subject,
        )
        message.template_id = _sendgrid_templates[template_name]
        message.dynamic_template_data = template_body
        message.tracking_settings = self.tracking_settings

        try:
            response = self.client.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)

            return response.status_code == HTTPStatus.ACCEPTED.value
        except Exception as e:
            print(e)  # pyright: ignore[reportAttributeAccessIssue]

            return False


def get_email_service() -> EmailService:
    if settings.email_provider == "sendgrid":
        return SendGridService()

    return MailpitService()


email_service = get_email_service()
