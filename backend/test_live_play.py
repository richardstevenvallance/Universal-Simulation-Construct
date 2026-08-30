from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_authenticity_requires_evidence():
    response = client.post("/api/authenticity/assess", json={"card_id": "base-charizard"})
    assert response.status_code == 400


def test_authenticity_returns_risk_and_passport():
    response = client.post(
        "/api/authenticity/assess",
        json={
            "card_id": "base-charizard",
            "hologram_motion_score": 0.95,
            "print_alignment_score": 0.92,
            "microprint_score": 0.9,
            "edge_core_score": 0.91,
            "image_quality": 0.95,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["counterfeit_risk"] == "low"
    assert body["passport_id"].startswith("dxp-")


def test_geo_context_is_location_adaptive():
    response = client.post(
        "/api/geo/context",
        json={"latitude": 53.5228, "longitude": -1.1285, "accuracy_m": 8.0, "source": "gps"},
    )
    assert response.status_code == 200
    assert response.json()["adaptive"] is True


def test_bluetooth_multiplayer_descriptor():
    response = client.post(
        "/api/multiplayer/sessions",
        json={"mode": "bluetooth_local", "game": "ar_battle", "max_players": 2},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "bluetooth_local"
    assert "Bluetooth" in body["transport"]


def test_geo_ar_scene_can_link_to_server_session():
    session = client.post(
        "/api/multiplayer/sessions",
        json={"mode": "server", "game": "ar_battle", "max_players": 2},
    ).json()
    response = client.post(
        "/api/ar/geo-scenes",
        json={
            "scene_type": "geo_encounter",
            "anchor": {"latitude": 51.5074, "longitude": -0.1278, "accuracy_m": 10, "source": "gps"},
            "card_ids": ["pikachu"],
            "multiplayer_session_id": session["id"],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["location_adaptive"] is True
    assert body["multiplayer_session_id"] == session["id"]


def test_rules_manifest_forbids_silent_staleness():
    response = client.get("/api/rules/current")
    assert response.status_code == 200
    assert "must not invent" in response.json()["policy"]
