# DexForge Architecture

## Product surfaces

1. Dex — Pokémon research and catalogue.
2. GO Companion — user-entered sessions, route/activity notes, teams and planning.
3. Scan — card identification and provisional grading.
4. Collection — owned copies, condition, decks and wanted cards.
5. Play — local TCG game state and progressively richer rules engine.

## Runtime split

### Sites frontend
A visual web/app experience can be built in Sites. It should treat the DexForge backend as the data/action authority and must not embed private provider secrets in the browser.

### Render backend
FastAPI is deployable from `backend/Dockerfile` through the root `render.yaml`. Render is the public API target for Sites and mobile clients.

### Raspberry Pi hub
The Pi can run the same API locally and later add persistent storage, camera/card-dock analysis, NFC, touchscreen, LEDs and speaker output.

## Data boundaries

- Pokémon research/card catalogue data should come from public/licensed sources with provenance and caching.
- Pokémon GO remains companion/user-owned data unless a legitimate public gameplay/account API becomes available.
- Grading is an original computer-assisted estimate and is never represented as an official PSA/CGC/BGS grade.
- The TCG rules engine should model structured operations rather than copy card artwork or proprietary presentation assets.

## TCG effect vocabulary

A future rules layer should encode effects such as `DRAW`, `SEARCH`, `ATTACH_ENERGY`, `DAMAGE`, `HEAL`, `SWITCH`, `STATUS`, `DISCARD`, and `COIN_FLIP` as testable state transitions.
