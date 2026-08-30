# Render + Repository Transfer

## Current staging location

Repository: `richardstevenvallance/Universal-Simulation-Construct`

Branch: `staging/dexforge-transfer-ready`

The USC `main` branch is deliberately untouched.

## Render-ready layout

- `render.yaml` — service blueprint
- `backend/Dockerfile` — container runtime
- `backend/requirements.txt` — Python dependencies
- `backend/main.py` — FastAPI entrypoint
- `/health` — Render health check

## Deploy from staging branch

When connecting Render before transfer, select this repository and branch and use the root `render.yaml` blueprint. Keep `autoDeploy: false` until the project has its own repository.

## Transfer into a dedicated repository later

Recommended final repository name: `DexForge-Pokemon-Companion`.

Safest transfer approaches:

1. Create the new empty repository and push/copy this staging branch as its `main` branch; or
2. Export this branch tree into the new repository and preserve the staging commit SHA in the migration note.

After transfer:

- change Render repository connection to the dedicated DexForge repository;
- keep `rootDir: backend`;
- set `DEXFORGE_ALLOWED_ORIGINS` to the final Sites origin;
- enable auto-deploy only after CI is required/passing;
- add persistent database/disk configuration before storing irreplaceable collection data in production.

## Important current limitation

Version 0.1 keeps GO sessions, decks and TCG match state in process memory. That is suitable for API/UI integration and testing but not permanent production collection storage. The persistence layer is intentionally the next backend milestone before live personal collection use.
