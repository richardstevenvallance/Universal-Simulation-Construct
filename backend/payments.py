from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

import httpx
from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/payments", tags=["payments"])

PaymentKind = Literal["marketplace_sale", "swap_balance"]
PaymentStatus = Literal[
    "requires_checkout",
    "checkout_created",
    "paid",
    "failed",
    "expired",
    "refunded",
]


class PaymentOrderCreate(BaseModel):
    buyer_id: str = Field(min_length=1, max_length=120)
    seller_id: str = Field(min_length=1, max_length=120)
    seller_connected_account_id: str = Field(min_length=4, max_length=255)
    amount_minor: int = Field(gt=0)
    currency: str = Field(default="gbp", min_length=3, max_length=3)
    kind: PaymentKind = "marketplace_sale"
    description: str = Field(default="DexForge card marketplace payment", min_length=1, max_length=240)
    related_id: str | None = Field(default=None, max_length=120)


ORDERS: dict[str, dict] = {}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def platform_fee_for(amount_minor: int) -> int:
    raw = os.getenv("DEXFORGE_PLATFORM_FEE_BPS", "0")
    try:
        basis_points = max(0, min(10_000, int(raw)))
    except ValueError:
        basis_points = 0
    return amount_minor * basis_points // 10_000


def create_internal_order(payload: PaymentOrderCreate) -> dict:
    order_id = f"pay_{uuid4().hex}"
    order = {
        "id": order_id,
        "buyer_id": payload.buyer_id,
        "seller_id": payload.seller_id,
        "seller_connected_account_id": payload.seller_connected_account_id,
        "amount_minor": payload.amount_minor,
        "currency": payload.currency.lower(),
        "kind": payload.kind,
        "description": payload.description,
        "related_id": payload.related_id,
        "platform_fee_minor": platform_fee_for(payload.amount_minor),
        "status": "requires_checkout",
        "provider": "stripe_connect",
        "provider_session_id": None,
        "created_at": _utc_now(),
        "updated_at": _utc_now(),
    }
    ORDERS[order_id] = order
    return order


@router.get("/provider")
def payment_provider_status():
    secret = bool(os.getenv("STRIPE_SECRET_KEY"))
    webhook = bool(os.getenv("STRIPE_WEBHOOK_SECRET"))
    success_url = bool(os.getenv("DEXFORGE_PAYMENT_SUCCESS_URL"))
    cancel_url = bool(os.getenv("DEXFORGE_PAYMENT_CANCEL_URL"))
    return {
        "provider": "stripe_connect",
        "checkout_mode": "stripe_hosted",
        "configured": secret and webhook and success_url and cancel_url,
        "raw_card_data_stored_by_dexforge": False,
        "persistent_payment_ledger_required_before_live_launch": True,
        "test_mode_recommended_until_database_migration": True,
    }


@router.post("/orders")
def create_payment_order(payload: PaymentOrderCreate):
    return create_internal_order(payload)


@router.get("/orders/{order_id}")
def get_payment_order(order_id: str):
    order = ORDERS.get(order_id)
    if not order:
        raise HTTPException(404, "Payment order not found.")
    return order


@router.post("/orders/{order_id}/checkout")
def create_checkout(order_id: str):
    order = ORDERS.get(order_id)
    if not order:
        raise HTTPException(404, "Payment order not found.")
    if order["status"] == "paid":
        raise HTTPException(409, "Payment order is already paid.")

    secret_key = os.getenv("STRIPE_SECRET_KEY")
    success_url = os.getenv("DEXFORGE_PAYMENT_SUCCESS_URL")
    cancel_url = os.getenv("DEXFORGE_PAYMENT_CANCEL_URL")
    if not secret_key or not success_url or not cancel_url:
        raise HTTPException(
            503,
            "Stripe Connect checkout is not configured. Set the server-side payment environment variables first.",
        )

    form = {
        "mode": "payment",
        "success_url": success_url,
        "cancel_url": cancel_url,
        "line_items[0][quantity]": "1",
        "line_items[0][price_data][currency]": order["currency"],
        "line_items[0][price_data][unit_amount]": str(order["amount_minor"]),
        "line_items[0][price_data][product_data][name]": order["description"],
        "payment_intent_data[transfer_data][destination]": order["seller_connected_account_id"],
        "metadata[order_id]": order_id,
        "payment_intent_data[metadata][order_id]": order_id,
    }
    if order["platform_fee_minor"]:
        form["payment_intent_data[application_fee_amount]"] = str(order["platform_fee_minor"])

    try:
        response = httpx.post(
            "https://api.stripe.com/v1/checkout/sessions",
            data=form,
            headers={"Authorization": f"Bearer {secret_key}"},
            timeout=15.0,
        )
        response.raise_for_status()
        session = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(502, "Payment provider could not create checkout.") from exc

    order["provider_session_id"] = session.get("id")
    order["status"] = "checkout_created"
    order["updated_at"] = _utc_now()
    return {
        "order_id": order_id,
        "status": order["status"],
        "checkout_url": session.get("url"),
        "provider": "stripe_connect",
    }


def _verify_stripe_signature(payload: bytes, signature_header: str, secret: str, tolerance: int = 300) -> None:
    pieces: dict[str, list[str]] = {}
    for item in signature_header.split(","):
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        pieces.setdefault(key.strip(), []).append(value.strip())
    try:
        timestamp = int(pieces["t"][0])
        signatures = pieces["v1"]
    except (KeyError, ValueError, IndexError) as exc:
        raise HTTPException(400, "Invalid Stripe signature header.") from exc

    if abs(int(time.time()) - timestamp) > tolerance:
        raise HTTPException(400, "Stripe webhook timestamp is outside the allowed tolerance.")

    signed_payload = f"{timestamp}.".encode() + payload
    expected = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()
    if not any(hmac.compare_digest(expected, candidate) for candidate in signatures):
        raise HTTPException(400, "Invalid Stripe webhook signature.")


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, stripe_signature: str | None = Header(default=None)):
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    if not webhook_secret:
        raise HTTPException(503, "Stripe webhook verification is not configured.")
    if not stripe_signature:
        raise HTTPException(400, "Missing Stripe-Signature header.")

    raw = await request.body()
    _verify_stripe_signature(raw, stripe_signature, webhook_secret)
    try:
        event = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise HTTPException(400, "Invalid webhook payload.") from exc

    event_type = event.get("type", "")
    obj = event.get("data", {}).get("object", {})
    metadata = obj.get("metadata") or {}
    order_id = metadata.get("order_id")
    order = ORDERS.get(order_id) if order_id else None

    if order:
        if event_type == "checkout.session.completed":
            order["status"] = "paid"
        elif event_type == "checkout.session.expired":
            order["status"] = "expired"
        elif event_type in {"payment_intent.payment_failed", "checkout.session.async_payment_failed"}:
            order["status"] = "failed"
        order["updated_at"] = _utc_now()

    return {"received": True, "event_type": event_type, "order_id": order_id}
