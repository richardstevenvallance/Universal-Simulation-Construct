from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class GradeMetrics(BaseModel):
    front_centering_lr: float = Field(ge=0, le=50)
    front_centering_tb: float = Field(ge=0, le=50)
    back_centering_lr: float | None = Field(default=None, ge=0, le=50)
    back_centering_tb: float | None = Field(default=None, ge=0, le=50)
    corner_defects: int = Field(default=0, ge=0, le=8)
    edge_defects: int = Field(default=0, ge=0, le=30)
    surface_defects: int = Field(default=0, ge=0, le=30)
    image_quality: float = Field(default=1.0, ge=0, le=1)


class GradeResult(BaseModel):
    provisional_grade: float
    label: str
    confidence: float
    reasons: list[str]
    disclaimer: str


class GoSession(BaseModel):
    title: str
    notes: str = ""
    distance_km: float = Field(default=0, ge=0)
    catches: int = Field(default=0, ge=0)
    raids: int = Field(default=0, ge=0)


class DeckCard(BaseModel):
    card_id: str
    name: str
    quantity: int = Field(ge=1, le=60)
    kind: Literal["pokemon", "trainer", "energy", "unknown"] = "unknown"


class Deck(BaseModel):
    name: str
    cards: list[DeckCard]


class MatchAction(BaseModel):
    action: Literal["draw", "end_turn", "damage", "heal"]
    player: int = Field(ge=1, le=2)
    amount: int = Field(default=0, ge=0)
