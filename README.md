# DexForge — Pokémon Companion + Raspberry Pi Hub

DexForge is an independent, unofficial Pokémon companion project. It is not affiliated with, endorsed by, or sponsored by Nintendo, The Pokémon Company, Game Freak, Niantic, Scopely, PSA, CGC, or BGS.

This staging branch is intentionally isolated from the Universal Simulation Construct main branch. It is structured so it can later be transferred into its own repository without changing the application architecture.

## Product surfaces

- Pokédex / research hub
- Pokémon GO companion module (no spoofing, automation, or private gameplay API)
- Card reader + provisional computer-assisted grader
- Collection + deck builder
- Local two-player TCG state engine
- Raspberry Pi home hub
- Sites-ready frontend API contract

## Render deployment

This branch includes `render.yaml` and a backend Dockerfile. Render should deploy the `backend` service and expose `/health` plus `/docs`.

## Raspberry Pi

The Pi can run the same FastAPI backend locally, cache research/card data, host scans and collections, and later drive a camera dock, touchscreen, NFC reader, LEDs, or a physical Pokédex shell.

## Quick start

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8765
```

Open `http://localhost:8765/docs`.

## Sites frontend contract

A Sites frontend can call:

- `GET /health`
- `POST /api/cards/grade`
- `GET|POST /api/go/sessions`
- `GET|PUT /api/decks/{deck_id}`
- `POST /api/matches/{match_id}/start`
- `POST /api/matches/{match_id}/action`
- `GET /api/matches/{match_id}`
- `GET /api/integrations/pokemon-go`

## Grading boundary

Any grade returned by DexForge is a provisional computer-assisted estimate, never an official PSA/CGC/BGS grade.
