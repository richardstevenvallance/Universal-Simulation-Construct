# DexForge — Pokémon Companion + Raspberry Pi Hub

©Jake Vallance 2025 ALL RIGHTS RESERVED

DexForge is an independent, unofficial Pokémon companion project. It is not affiliated with, endorsed by, or sponsored by Nintendo, The Pokémon Company, Game Freak, Niantic, Scopely, PSA, CGC, BGS, Stripe, or any grading/payment provider.

This staging branch is intentionally isolated from the Universal Simulation Construct main branch. It is structured so it can later be transferred into its own repository without changing the application architecture.

## Product surfaces

- Pokédex / research hub
- Pokémon GO real-time **companion** using consented device location + legitimate public/current signals (no spoofing, automation, or private gameplay API)
- Card reader + provisional computer-assisted grader
- Multi-signal counterfeit-risk / hologram reader contract
- DexForge provenance passport / digital twin for scanned cards
- Collection + deck builder
- Swaps + card marketplace
- Stripe Connect payment contract using provider-hosted checkout
- Full/current-rules version manifest with source/effective-date/hash requirements
- Local Bluetooth/BLE friend play contract + server-authoritative multiplayer
- Local two-player TCG state engine
- Provider-neutral AR scenes for card inspection, tabletop battles, galleries and geo-adaptive experiences
- Raspberry Pi home hub / grading dock / offline tournament server
- Sites-ready frontend API contract

## Render deployment

This branch includes `render.yaml` and a backend Dockerfile. Render should deploy the `backend` service and expose `/health` plus `/docs`.

`autoDeploy` remains intentionally disabled while DexForge is staged inside the temporary USC repository.

## Raspberry Pi

The Pi can run the same FastAPI backend locally, cache research/card/rules data, host scans and collections, and later drive a calibrated camera dock, diffuse multi-angle lighting, optional UV capture, weight/thickness sensors, touchscreen, NFC reader, LEDs, speaker, or a physical Pokédex shell.

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
- `POST /api/authenticity/assess`
- `GET /api/rules/current`
- `POST /api/geo/context`
- `GET /api/live/pokemon-go/capabilities`
- `POST|GET /api/multiplayer/sessions*`
- `POST /api/ar/geo-scenes`
- `GET|POST /api/go/sessions`
- `GET|PUT /api/decks/{deck_id}`
- `/api/swaps/*` for listings, offers, card-plus-cash swaps and purchases
- `/api/payments/*` for payment orders, provider status, Checkout session creation and verified Stripe webhooks
- `/api/ar/*` for AR capabilities and shared scene descriptors
- `POST /api/matches/{match_id}/start`
- `POST /api/matches/{match_id}/action`
- `GET /api/matches/{match_id}`
- `GET /api/integrations/pokemon-go`

See `docs/AUTHENTICITY_RULES_GEO_LIVE.md`, `docs/MARKETPLACE_PAYMENTS_AR.md` and `docs/SITES_FRONTEND_CONTRACT.md` before wiring the frontend.

## Authenticity boundary

DexForge authenticity output is a counterfeit-risk assessment built from multiple observations such as holographic motion, print alignment, microprint, edge/core appearance, optional UV response and controlled capture quality. It is not a guarantee of authenticity or an official certification. High-value transfers should re-scan the physical card against its DexForge passport.

## Rules boundary

DexForge must version and verify the current official rules source, effective date and content hash. It must not silently retain stale rules or invent competitive rules.

## Location / Pokémon GO boundary

DexForge can use the user's real-time device GNSS/GPS/network location with permission and adapt its own AR/companion experiences to any valid geo coordinate. If satellite imagery is shown, it comes from a licensed imagery/map provider; it is not described as a live satellite feed. DexForge does not use private Pokémon GO gameplay/account endpoints, spoof location, or automate gameplay.

## Payment boundary

DexForge never stores raw card numbers or CVC data. Checkout is provider-hosted. The current swap/payment ledger is in memory and **must be migrated to a persistent transactional database before any real-money launch**.

## AR / multiplayer boundary

Sites can begin with 3D/progressive-enhancement experiences. Native mobile can later provide Bluetooth/BLE local pairing, richer camera/location access and persistent world AR. Server mode keeps authoritative match state online; local Bluetooth mode uses the same rules/state contracts offline or nearby.

## Grading boundary

Any grade returned by DexForge is a provisional computer-assisted estimate, never an official PSA/CGC/BGS grade.

## Copyright

See `COPYRIGHT.md`. The copyright notice applies to original DexForge materials only; third-party Pokémon-related intellectual property remains with its respective owners.
