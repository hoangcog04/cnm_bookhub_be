import stripe as _stripe
from stripe import PaymentIntent

from cnm_bookhub_be.settings import settings


class _StripeService:
    def __init__(self) -> None:
        _stripe.api_key = settings.stripe_secret_key

    async def create_payment_intent(
        self, amount: int, currency: str = "vnd"
    ) -> PaymentIntent:
        return _stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            automatic_payment_methods={"enabled": True},
        )


stripe_service = _StripeService()
