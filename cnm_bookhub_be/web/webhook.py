import json

import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from cnm_bookhub_be.db.dao.order_dao import OrderDAO
from cnm_bookhub_be.settings import settings

router = APIRouter()

endpoint_secret = settings.stripe_webhook_secret


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature"),
    order_dao: OrderDAO = Depends(),
) -> JSONResponse:
    payload = await request.body()
    event = None

    try:
        event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")  # noqa: B904

    if endpoint_secret:
        if not stripe_signature:
            raise HTTPException(status_code=400, detail="Missing signature")

        try:
            event = stripe.Webhook.construct_event(
                payload, stripe_signature, endpoint_secret
            )
        except stripe.error.SignatureVerificationError as e:  # pyright: ignore[reportPrivateImportUsage]
            print("⚠️  Webhook signature verification failed." + str(e))
            raise HTTPException(status_code=400, detail="Invalid signature")  # noqa: B904

    # Handle the event
    if event.type == "payment_intent.succeeded":
        payment_intent = event.data.object
        await order_dao.mark_order_as_processed(payment_intent["id"])
        print(f"PaymentIntent {payment_intent['id']} succeeded")

    elif event.type == "payment_method.attached":
        payment_method = event.data.object
        print(f"PaymentMethod {payment_method['id']} attached")

    # ... handle other event types
    else:
        print(f"Unhandled event type {event.type}")

    return JSONResponse(content={"status": "success"}, status_code=200)
