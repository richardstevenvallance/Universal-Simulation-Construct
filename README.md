# DexForge — Pokémon Companion + Raspberry Pi Hub

DexForge is an independent, unofficial Pokémon companion project. It is not affiliated with, endorsed by, or sponsored by Nintendo, The Pokémon Company, Game Freak, Niantic, Scopely, PSA, CGC, BGS, or Stripe.

This staging branch is intentionally isolated from the Universal Simulation Construct main branch. It is structured so it can later be transferred into its own repository without changing the application architecture.

## Product surfaces

- Pokédex / research hub
- Pokémon GO companion module (no spoofing, automation, or private gameplay API)
- Card reader + provisional computer-assisted grader
- Collection + deck builder
- Swaps + card marketplace
- Stripe Connect payment contract using provider-hosted checkout
- Local two-player TCG state engine
- Provider-neutral AR scene contract for card inspection, tabletop play, galleries and location AR
- Raspberry Pi home hub
- Sites-ready frontend API contract

## Render deployment

This branch includes `render.yaml` and a backend Dockerfile. Render should deploy the `backend` service and expose `/health` plus `/docs`.

`autoDeploy` remains intentionally disabled while DexForge is staged inside the temporary USC repository.

## Raspberry Pi

The Pi can run the same FastAPI backend locally, cache research/card data, host scans and collections, and later drive a camera dock, touchscreen, NFC reader, LEDs, speaker, or a physical Pokédex shell.

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

Core API groups now include:

- `GET /health`
- `POST /api/cards/grade`
- `GET|POST /api/go/sessions`
- `GET|PUT /api/decks/{deck_id}`
- `/api/swaps/*` for listings, offers, card-plus-cash swaps and purchases
- `/api/payments/*` for payment orders, provider status, Checkout session creation and verified Stripe webhooks
- `/api/ar/*` for AR capabilities and shared scene descriptors
- `POST /api/matches/{match_id}/start`
- `POST /api/matches/{match_id}/action`
- `GET /api/matches/{match_id}`
- `GET /api/integrations/pokemon-go`

See `docs/MARKETPLACE_PAYMENTS_AR.md` and `docs/SITES_FRONTEND_CONTRACT.md` before wiring the frontend.

## Payment boundary

DexForge never stores raw card numbers or CVC data. Checkout is provider-hosted. The current swap/payment ledger is in memory and **must be migrated to a persistent transactional database before any real-money launch**.

## AR boundary

Sites can begin with 3D/progressive-enhancement experiences. Persistent location AR is designed for a later native Unity + Niantic Spatial 4.x client consuming the same `dexforge.ar-scene.v1` contract. Provider secrets stay out of public frontend bundles.

## Grading boundary

Any grade returned by DexForge is a provisional computer-assisted estimate, never an official PSA/CGC/BGS grade.
