# Sites Frontend Contract

The Sites project should be presentation + interaction only. DexForge backend owns state and grading logic.

## Public API base

Use the Render service URL during public deployment, or the Raspberry Pi LAN URL while at home.

## Endpoints

### Health
`GET /health`

### Card grading
`POST /api/cards/grade`

Example body:

```json
{
  "front_centering_lr": 49,
  "front_centering_tb": 50,
  "back_centering_lr": 48,
  "back_centering_tb": 49,
  "corner_defects": 0,
  "edge_defects": 0,
  "surface_defects": 0,
  "image_quality": 0.95
}
```

The UI must visibly label the result as provisional and show confidence/reasons.

### GO companion
- `POST /api/go/sessions`
- `GET /api/go/sessions`

Do not expose spoofing, automation or undocumented gameplay/account operations.

### Decks
- `PUT /api/decks/{deck_id}`
- `GET /api/decks/{deck_id}`

### TCG game state
- `POST /api/matches/{match_id}/start`
- `POST /api/matches/{match_id}/action`
- `GET /api/matches/{match_id}`

### GO integration status
`GET /api/integrations/pokemon-go`

The Sites UI can use this endpoint to explain what the companion can and cannot do.

## CORS

Set Render environment variable `DEXFORGE_ALLOWED_ORIGINS` to the exact Sites origin once the Sites URL exists. Multiple origins are comma-separated.

## Browser secrets

Do not place provider API keys, private tokens, grading-service credentials, or GitHub/Render credentials into Sites client code. Any future protected connector should be called server-side through DexForge.
