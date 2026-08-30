from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/ar", tags=["ar"])

ARMode = Literal[
    "card_inspection",
    "tabletop_battle",
    "collection_gallery",
    "location_anchor",
    "go_companion_overlay",
]


class ARAsset(BaseModel):
    asset_ref: str = Field(min_length=1, max_length=255)
    canonical_id: str | None = Field(default=None, max_length=160)
    label: str = Field(default="", max_length=200)
    scale: float = Field(default=1.0, gt=0, le=100)


class ARAnchor(BaseModel):
    kind: Literal["screen", "table", "image", "location"] = "table"
    provider_anchor_id: str | None = Field(default=None, max_length=255)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)


class ARExperienceCreate(BaseModel):
    owner_id: str = Field(min_length=1, max_length=120)
    title: str = Field(min_length=1, max_length=200)
    mode: ARMode
    assets: list[ARAsset] = Field(default_factory=list, max_length=100)
    anchor: ARAnchor = Field(default_factory=ARAnchor)
    shared: bool = False


EXPERIENCES: dict[str, dict] = {}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.get("/capabilities")
def ar_capabilities():
    return {
        "contract": "dexforge.ar-scene.v1",
        "renderers": {
            "sites_web": {
                "supported": True,
                "mode": "3d_preview_and_device_capability_progressive_enhancement",
            },
            "unity_niantic_spatial": {
                "supported": True,
                "recommended_version_family": "4.x",
                "features": [
                    "AR Foundation integration",
                    "VPS/VPS2 location anchors",
                    "depth",
                    "occlusion",
                    "meshing",
                    "semantic/spatial effects",
                ],
            },
        },
        "private_provider_token_in_frontend": False,
        "precise_location_public_by_default": False,
    }


@router.post("/experiences")
def create_ar_experience(payload: ARExperienceCreate):
    if payload.anchor.kind == "location":
        if payload.anchor.latitude is None or payload.anchor.longitude is None:
            raise HTTPException(400, "Location anchors require latitude and longitude.")

    experience_id = f"ar_{uuid4().hex}"
    record = {
        "id": experience_id,
        **payload.model_dump(),
        "contract": "dexforge.ar-scene.v1",
        "created_at": _now(),
        "updated_at": _now(),
    }
    EXPERIENCES[experience_id] = record
    return record


@router.get("/experiences")
def list_ar_experiences(shared_only: bool = False):
    items = list(EXPERIENCES.values())
    if shared_only:
        items = [item for item in items if item["shared"]]
    return {"experiences": items}


@router.get("/experiences/{experience_id}")
def get_ar_experience(experience_id: str):
    record = EXPERIENCES.get(experience_id)
    if not record:
        raise HTTPException(404, "AR experience not found.")
    return record
