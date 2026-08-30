from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api")


class AuthenticityScan(BaseModel):
    card_id: str
    hologram_motion_score: float | None = Field(default=None, ge=0, le=1)
    print_alignment_score: float | None = Field(default=None, ge=0, le=1)
    microprint_score: float | None = Field(default=None, ge=0, le=1)
    edge_core_score: float | None = Field(default=None, ge=0, le=1)
    uv_response_score: float | None = Field(default=None, ge=0, le=1)
    image_quality: float = Field(default=1.0, ge=0, le=1)


class GeoContext(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    accuracy_m: float = Field(ge=0)
    source: Literal["gps", "network", "manual"] = "gps"
    captured_at: datetime | None = None


class MultiplayerSessionCreate(BaseModel):
    mode: Literal["bluetooth_local", "server"]
    game: Literal["tcg", "ar_battle"] = "tcg"
    max_players: int = Field(default=2, ge=2, le=4)
    geo: GeoContext | None = None


class ARGeoSceneCreate(BaseModel):
    scene_type: Literal["card_inspection", "tabletop_battle", "collection_gallery", "geo_encounter"]
    anchor: GeoContext | None = None
    card_ids: list[str] = []
    multiplayer_session_id: str | None = None


MULTIPLAYER: dict[str, dict] = {}
AR_GEO_SCENES: dict[str, dict] = {}


def _weighted(values: list[float | None]) -> tuple[float, int]:
    present = [v for v in values if v is not None]
    if not present:
        return 0.0, 0
    return sum(present) / len(present), len(present)


@router.post("/authenticity/assess")
def assess_authenticity(scan: AuthenticityScan):
    mean, count = _weighted([
        scan.hologram_motion_score,
        scan.print_alignment_score,
        scan.microprint_score,
        scan.edge_core_score,
        scan.uv_response_score,
    ])
    if count == 0:
        raise HTTPException(400, "At least one authenticity observation is required.")

    adjusted = mean * scan.image_quality
    if adjusted >= 0.82:
        risk = "low"
    elif adjusted >= 0.60:
        risk = "medium"
    else:
        risk = "high"

    confidence = round(min(0.98, scan.image_quality * (count / 5)), 2)
    passport_id = f"dxp-{uuid4()}"
    return {
        "contract": "dexforge.authenticity.v1",
        "card_id": scan.card_id,
        "counterfeit_risk": risk,
        "confidence": confidence,
        "passport_id": passport_id,
        "observations_used": count,
        "disclaimer": "Counterfeit-risk assessment only; not a guarantee of authenticity or an official certification.",
    }


@router.get("/rules/current")
def current_rules_manifest():
    return {
        "contract": "dexforge.rules-manifest.v1",
        "status": "source_required",
        "policy": "DexForge must ingest and version the current official rules source; it must not invent or silently retain stale rules.",
        "required_fields": ["source_url", "effective_date", "retrieved_at", "ruleset_hash", "format"],
        "live_tournament_rules": "must be verified against the current official source before competitive use",
    }


@router.post("/geo/context")
def normalize_geo_context(context: GeoContext):
    captured = context.captured_at or datetime.now(timezone.utc)
    return {
        "contract": "dexforge.geo-context.v1",
        **context.model_dump(exclude={"captured_at"}),
        "captured_at": captured.isoformat(),
        "adaptive": True,
        "notes": [
            "Use device GNSS/network location with user permission.",
            "Satellite map imagery is provider imagery, not a live satellite feed.",
        ],
    }


@router.post("/multiplayer/sessions")
def create_multiplayer_session(request: MultiplayerSessionCreate):
    session_id = f"dxm-{uuid4()}"
    transport = (
        "native Bluetooth/BLE peer link; backend supplies shared rules/state contract"
        if request.mode == "bluetooth_local"
        else "DexForge server authoritative session"
    )
    item = {
        "contract": "dexforge.multiplayer.v1",
        "id": session_id,
        "mode": request.mode,
        "game": request.game,
        "max_players": request.max_players,
        "transport": transport,
        "geo": request.geo.model_dump(mode="json") if request.geo else None,
        "status": "open",
    }
    MULTIPLAYER[session_id] = item
    return item


@router.get("/multiplayer/sessions/{session_id}")
def get_multiplayer_session(session_id: str):
    if session_id not in MULTIPLAYER:
        raise HTTPException(404, "Multiplayer session not found.")
    return MULTIPLAYER[session_id]


@router.post("/ar/geo-scenes")
def create_geo_scene(request: ARGeoSceneCreate):
    if request.multiplayer_session_id and request.multiplayer_session_id not in MULTIPLAYER:
        raise HTTPException(404, "Multiplayer session not found.")
    scene_id = f"dxar-{uuid4()}"
    item = {
        "contract": "dexforge.ar-geo-scene.v1",
        "id": scene_id,
        "scene_type": request.scene_type,
        "anchor": request.anchor.model_dump(mode="json") if request.anchor else None,
        "card_ids": request.card_ids,
        "multiplayer_session_id": request.multiplayer_session_id,
        "location_adaptive": request.anchor is not None,
    }
    AR_GEO_SCENES[scene_id] = item
    return item


@router.get("/live/pokemon-go/capabilities")
def pokemon_go_live_capabilities():
    return {
        "contract": "dexforge.pokemon-go-live.v1",
        "real_time_location": True,
        "device_location_sources": ["gps", "network"],
        "allowed_live_inputs": [
            "user device location",
            "official public event/news feeds when available",
            "user-entered or consented community observations",
        ],
        "not_supported": [
            "private Pokémon GO gameplay/account API",
            "location spoofing",
            "automated catching or gameplay",
            "claiming a map tile is a live satellite camera feed",
        ],
    }
