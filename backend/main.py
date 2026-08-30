from __future__ import annotations

import os
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from grading import provisional_grade
from models import Deck, GoSession, GradeMetrics, GradeResult, MatchAction

app = FastAPI(
    title="DexForge API",
    version="0.1.0",
    description="Independent Pokémon companion + Raspberry Pi hub.",
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv("DEXFORGE_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]
if allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )

GO_SESSIONS: list[dict] = []
DECKS: dict[str, dict] = {}
MATCHES: dict[str, dict] = {}


@app.get("/health")
def health():
    return {"status": "ok", "service": "dexforge", "version": "0.1.0"}


@app.post("/api/cards/grade", response_model=GradeResult)
def grade_card(metrics: GradeMetrics):
    return provisional_grade(metrics)


@app.post("/api/go/sessions")
def create_go_session(session: GoSession):
    item = {
        "id": len(GO_SESSIONS) + 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        **session.model_dump(),
    }
    GO_SESSIONS.append(item)
    return item


@app.get("/api/go/sessions")
def list_go_sessions():
    return {"sessions": GO_SESSIONS}


@app.put("/api/decks/{deck_id}")
def save_deck(deck_id: str, deck: Deck):
    total = sum(card.quantity for card in deck.cards)
    if total > 60:
        raise HTTPException(400, "Deck cannot exceed 60 cards.")
    DECKS[deck_id] = {"id": deck_id, "total_cards": total, **deck.model_dump()}
    return DECKS[deck_id]


@app.get("/api/decks/{deck_id}")
def get_deck(deck_id: str):
    if deck_id not in DECKS:
        raise HTTPException(404, "Deck not found.")
    return DECKS[deck_id]


@app.post("/api/matches/{match_id}/start")
def start_match(match_id: str):
    state = {
        "id": match_id,
        "turn": 1,
        "active_player": 1,
        "players": {
            "1": {"hand": 7, "damage": 0},
            "2": {"hand": 7, "damage": 0},
        },
        "log": ["Match started"],
    }
    MATCHES[match_id] = state
    return state


@app.post("/api/matches/{match_id}/action")
def match_action(match_id: str, action: MatchAction):
    state = MATCHES.get(match_id)
    if not state:
        raise HTTPException(404, "Match not found.")

    player = state["players"][str(action.player)]
    if action.action == "draw":
        amount = max(1, action.amount or 1)
        player["hand"] += amount
        state["log"].append(f"Player {action.player} drew {amount}")
    elif action.action == "damage":
        player["damage"] += action.amount
        state["log"].append(f"Player {action.player} took {action.amount} damage")
    elif action.action == "heal":
        player["damage"] = max(0, player["damage"] - action.amount)
        state["log"].append(f"Player {action.player} healed {action.amount}")
    elif action.action == "end_turn":
        state["active_player"] = 2 if state["active_player"] == 1 else 1
        state["turn"] += 1
        state["log"].append(f"Turn ended; active player is {state['active_player']}")
    return state


@app.get("/api/matches/{match_id}")
def get_match(match_id: str):
    if match_id not in MATCHES:
        raise HTTPException(404, "Match not found.")
    return MATCHES[match_id]


@app.get("/api/integrations/pokemon-go")
def pokemon_go_integration_status():
    return {
        "mode": "companion_only",
        "private_gameplay_api": False,
        "location_spoofing": False,
        "automation": False,
        "supported": [
            "user-entered sessions",
            "route/activity notes",
            "collection planning",
            "raid/team notes",
            "future legitimate public integrations",
        ],
    }
