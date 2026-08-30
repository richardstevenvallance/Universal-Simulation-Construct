from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from payments import PaymentOrderCreate, create_internal_order

router = APIRouter(prefix="/api/swaps", tags=["swaps", "marketplace"])

ListingMode = Literal["swap_only", "sale_only", "sale_or_swap"]
ListingStatus = Literal["open", "reserved", "completed", "withdrawn"]
OfferStatus = Literal[
    "pending",
    "declined",
    "accepted_pending_exchange",
    "accepted_pending_payment",
    "completed",
]


class SwapCard(BaseModel):
    card_id: str = Field(min_length=1, max_length=160)
    name: str = Field(min_length=1, max_length=200)
    condition: str = Field(default="ungraded", min_length=1, max_length=100)
    provisional_grade: float | None = Field(default=None, ge=1, le=10)


class ListingCreate(BaseModel):
    owner_id: str = Field(min_length=1, max_length=120)
    card: SwapCard
    mode: ListingMode = "swap_only"
    asking_amount_minor: int | None = Field(default=None, ge=0)
    currency: str = Field(default="gbp", min_length=3, max_length=3)
    seller_connected_account_id: str | None = Field(default=None, max_length=255)
    notes: str = Field(default="", max_length=500)


class OfferCreate(BaseModel):
    listing_id: str = Field(min_length=1, max_length=120)
    proposer_id: str = Field(min_length=1, max_length=120)
    offered_cards: list[SwapCard] = Field(default_factory=list, max_length=50)
    cash_to_owner_minor: int = Field(default=0, ge=0)
    note: str = Field(default="", max_length=500)


class AcceptOffer(BaseModel):
    owner_id: str = Field(min_length=1, max_length=120)


class BuyListing(BaseModel):
    buyer_id: str = Field(min_length=1, max_length=120)


LISTINGS: dict[str, dict] = {}
OFFERS: dict[str, dict] = {}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.post("/listings")
def create_listing(payload: ListingCreate):
    if payload.mode in {"sale_only", "sale_or_swap"}:
        if not payload.asking_amount_minor or payload.asking_amount_minor <= 0:
            raise HTTPException(400, "Sale listings require a positive asking amount.")
        if not payload.seller_connected_account_id:
            raise HTTPException(400, "Sale listings require a connected seller payment account.")

    listing_id = f"lst_{uuid4().hex}"
    listing = {
        "id": listing_id,
        **payload.model_dump(),
        "currency": payload.currency.lower(),
        "status": "open",
        "created_at": _now(),
        "updated_at": _now(),
    }
    LISTINGS[listing_id] = listing
    return listing


@router.get("/listings")
def list_open_listings():
    return {"listings": [item for item in LISTINGS.values() if item["status"] == "open"]}


@router.get("/listings/{listing_id}")
def get_listing(listing_id: str):
    listing = LISTINGS.get(listing_id)
    if not listing:
        raise HTTPException(404, "Listing not found.")
    return listing


@router.post("/offers")
def create_offer(payload: OfferCreate):
    listing = LISTINGS.get(payload.listing_id)
    if not listing or listing["status"] != "open":
        raise HTTPException(404, "Open listing not found.")
    if listing["mode"] == "sale_only" and payload.offered_cards:
        raise HTTPException(400, "This listing is sale-only.")
    if listing["mode"] == "swap_only" and payload.cash_to_owner_minor and not payload.offered_cards:
        raise HTTPException(400, "Swap-only listings require at least one offered card.")
    if payload.proposer_id == listing["owner_id"]:
        raise HTTPException(400, "You cannot make an offer on your own listing.")

    offer_id = f"ofr_{uuid4().hex}"
    offer = {
        "id": offer_id,
        **payload.model_dump(),
        "status": "pending",
        "payment_order_id": None,
        "created_at": _now(),
        "updated_at": _now(),
    }
    OFFERS[offer_id] = offer
    return offer


@router.get("/offers/{offer_id}")
def get_offer(offer_id: str):
    offer = OFFERS.get(offer_id)
    if not offer:
        raise HTTPException(404, "Offer not found.")
    return offer


@router.post("/offers/{offer_id}/accept")
def accept_offer(offer_id: str, payload: AcceptOffer):
    offer = OFFERS.get(offer_id)
    if not offer:
        raise HTTPException(404, "Offer not found.")
    if offer["status"] != "pending":
        raise HTTPException(409, "Offer is no longer pending.")

    listing = LISTINGS.get(offer["listing_id"])
    if not listing or listing["status"] != "open":
        raise HTTPException(409, "Listing is no longer open.")
    if payload.owner_id != listing["owner_id"]:
        raise HTTPException(403, "Only the listing owner can accept the offer.")

    if offer["cash_to_owner_minor"] > 0:
        seller_account = listing.get("seller_connected_account_id")
        if not seller_account:
            raise HTTPException(
                409,
                "This swap includes a cash balance, but the listing owner has no connected payment account.",
            )
        order = create_internal_order(
            PaymentOrderCreate(
                buyer_id=offer["proposer_id"],
                seller_id=listing["owner_id"],
                seller_connected_account_id=seller_account,
                amount_minor=offer["cash_to_owner_minor"],
                currency=listing["currency"],
                kind="swap_balance",
                description=f"DexForge swap balance for {listing['card']['name']}",
                related_id=offer_id,
            )
        )
        offer["payment_order_id"] = order["id"]
        offer["status"] = "accepted_pending_payment"
    else:
        offer["status"] = "accepted_pending_exchange"

    listing["status"] = "reserved"
    listing["updated_at"] = _now()
    offer["updated_at"] = _now()
    return offer


@router.post("/listings/{listing_id}/buy")
def buy_listing(listing_id: str, payload: BuyListing):
    listing = LISTINGS.get(listing_id)
    if not listing or listing["status"] != "open":
        raise HTTPException(404, "Open listing not found.")
    if listing["mode"] == "swap_only":
        raise HTTPException(400, "This listing is swap-only.")
    if payload.buyer_id == listing["owner_id"]:
        raise HTTPException(400, "You cannot buy your own listing.")

    order = create_internal_order(
        PaymentOrderCreate(
            buyer_id=payload.buyer_id,
            seller_id=listing["owner_id"],
            seller_connected_account_id=listing["seller_connected_account_id"],
            amount_minor=listing["asking_amount_minor"],
            currency=listing["currency"],
            kind="marketplace_sale",
            description=f"DexForge marketplace purchase: {listing['card']['name']}",
            related_id=listing_id,
        )
    )
    listing["status"] = "reserved"
    listing["updated_at"] = _now()
    return {"listing_id": listing_id, "payment_order": order}
