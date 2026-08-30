from fastapi.testclient import TestClient

from ar import EXPERIENCES
from main import app
from marketplace import LISTINGS, OFFERS
from payments import ORDERS

client = TestClient(app)


def setup_function():
    LISTINGS.clear()
    OFFERS.clear()
    ORDERS.clear()
    EXPERIENCES.clear()


def test_card_for_card_swap_acceptance():
    listing = client.post(
        "/api/swaps/listings",
        json={
            "owner_id": "seller-1",
            "card": {"card_id": "sv-001", "name": "Example ex", "condition": "near mint"},
            "mode": "swap_only",
        },
    ).json()

    offer = client.post(
        "/api/swaps/offers",
        json={
            "listing_id": listing["id"],
            "proposer_id": "buyer-1",
            "offered_cards": [
                {"card_id": "swsh-002", "name": "Example V", "condition": "near mint"}
            ],
        },
    ).json()

    accepted = client.post(
        f"/api/swaps/offers/{offer['id']}/accept",
        json={"owner_id": "seller-1"},
    )
    assert accepted.status_code == 200
    assert accepted.json()["status"] == "accepted_pending_exchange"


def test_cash_balanced_swap_creates_payment_order():
    listing = client.post(
        "/api/swaps/listings",
        json={
            "owner_id": "seller-1",
            "card": {"card_id": "sv-010", "name": "Example illustration rare"},
            "mode": "sale_or_swap",
            "asking_amount_minor": 5000,
            "currency": "gbp",
            "seller_connected_account_id": "acct_test_seller_1",
        },
    ).json()

    offer = client.post(
        "/api/swaps/offers",
        json={
            "listing_id": listing["id"],
            "proposer_id": "buyer-1",
            "offered_cards": [
                {"card_id": "sv-011", "name": "Example full art"}
            ],
            "cash_to_owner_minor": 1500,
        },
    ).json()

    accepted = client.post(
        f"/api/swaps/offers/{offer['id']}/accept",
        json={"owner_id": "seller-1"},
    ).json()

    assert accepted["status"] == "accepted_pending_payment"
    assert accepted["payment_order_id"] in ORDERS
    assert ORDERS[accepted["payment_order_id"]]["amount_minor"] == 1500


def test_payment_provider_never_claims_raw_card_storage():
    response = client.get("/api/payments/provider")
    assert response.status_code == 200
    assert response.json()["raw_card_data_stored_by_dexforge"] is False


def test_ar_location_anchor_requires_coordinates():
    response = client.post(
        "/api/ar/experiences",
        json={
            "owner_id": "user-1",
            "title": "Outdoor encounter",
            "mode": "location_anchor",
            "anchor": {"kind": "location"},
        },
    )
    assert response.status_code == 400


def test_ar_tabletop_experience_contract():
    response = client.post(
        "/api/ar/experiences",
        json={
            "owner_id": "user-1",
            "title": "Tabletop battle",
            "mode": "tabletop_battle",
            "assets": [{"asset_ref": "card:sv-001", "label": "Example card"}],
            "anchor": {"kind": "table"},
        },
    )
    assert response.status_code == 200
    assert response.json()["contract"] == "dexforge.ar-scene.v1"
