# Sites Frontend Contract

The Sites project should be presentation + interaction only. DexForge backend owns state, grading logic, marketplace transitions, payment orders and AR scene descriptors.

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

### Swaps and marketplace
- `POST /api/swaps/listings`
- `GET /api/swaps/listings`
- `GET /api/swaps/listings/{listing_id}`
- `POST /api/swaps/offers`
- `GET /api/swaps/offers/{offer_id}`
- `POST /api/swaps/offers/{offer_id}/accept`
- `POST /api/swaps/listings/{listing_id}/buy`

Sites should present three explicit listing types: swap only, sale only, and sale or swap. A swap offer may contain cards plus an optional cash balance. The backend, not the browser, determines the resulting state.

### Payments
- `GET /api/payments/provider`
- `POST /api/payments/orders`
- `GET /api/payments/orders/{order_id}`
- `POST /api/payments/orders/{order_id}/checkout`

The Checkout endpoint returns a provider-hosted URL. Redirect the user to that URL. Sites must **never** collect or transmit raw card numbers/CVC values to DexForge.

`POST /api/payments/webhooks/stripe` is provider-to-server only and must never be called from Sites.

Do not enable real-money UI until the backend payment ledger has moved from memory to a persistent transactional database and authentication/ownership controls are in place.

### AR
- `GET /api/ar/capabilities`
- `POST /api/ar/experiences`
- `GET /api/ar/experiences`
- `GET /api/ar/experiences/{experience_id}`

Sites can initially render card/object 3D previews from the `dexforge.ar-scene.v1` descriptor and progressively enhance supported devices. Persistent VPS/VPS2 location AR is expected to run in a later native Unity/Niantic Spatial client using the same backend scene IDs.

Never place a Niantic Spatial developer token in Sites code. Precise locations are private by default.

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

Do not place payment-provider secret keys, webhook secrets, Niantic developer tokens, private grading-service credentials, GitHub credentials, or Render credentials into Sites client code. Any protected connector must be called server-side through DexForge.
