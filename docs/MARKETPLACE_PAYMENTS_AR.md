# Swaps, Marketplace, Payments and AR

## Swaps and marketplace

DexForge supports three listing modes:

- `swap_only`
- `sale_only`
- `sale_or_swap`

A swap offer can contain one or more cards plus an optional cash balance paid to the listing owner. Accepting a pure card swap moves the offer into `accepted_pending_exchange`. Accepting an offer with a cash balance creates a payment order and moves the offer into `accepted_pending_payment`.

The current staging implementation uses an in-memory ledger. This is suitable for API/UI development and CI only. Before real users or real money are enabled, listings, offers, payment orders, webhook events and fulfilment state must be migrated to a transactional persistent database.

## Payments

The production payment architecture is Stripe Connect with Stripe-hosted Checkout.

DexForge does **not** accept or store raw card numbers, CVCs or payment credentials. The frontend requests a checkout session from the backend and redirects the user to the provider-hosted checkout page.

Server-side environment variables:

- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `DEXFORGE_PAYMENT_SUCCESS_URL`
- `DEXFORGE_PAYMENT_CANCEL_URL`
- `DEXFORGE_PLATFORM_FEE_BPS`

The backend creates destination-style marketplace payments by attaching the seller's connected account to the PaymentIntent created through Checkout. An optional application fee can be configured in basis points.

Webhook signatures are verified before payment state is updated. Webhooks currently update the in-memory order ledger; this must become database-backed before live launch.

Recommended launch sequence:

1. persistent database and immutable transaction/audit IDs
2. user authentication and ownership checks
3. Stripe Connect seller onboarding
4. Stripe test mode
5. webhook replay/idempotency tests
6. refund/dispute/chargeback states
7. shipping or in-person handover confirmation
8. production review and live payments

Do not describe the workflow as regulated escrow unless a qualified payment/legal provider is actually supplying an escrow service. DexForge should describe states such as payment pending, paid, dispatched, received and disputed instead.

## AR

The backend exposes `dexforge.ar-scene.v1`, a provider-neutral scene contract. This lets different clients render the same DexForge AR object without changing canonical collection/card data.

Initial modes:

- card inspection
- tabletop battle
- collection gallery
- location anchor
- GO companion overlay

### Sites/web

Sites can begin with 3D card/object previews and progressively enhance on devices with suitable browser capabilities. The web frontend should never receive a private Niantic developer token.

### Native AR

For persistent real-world/location AR, the recommended native path is Unity + Niantic Spatial SDK 4.x. The current Niantic SDK extends AR Foundation and supports VPS/VPS2 anchoring, depth, occlusion and meshing.

Precise location data is private by default. A location-based experience should only become shared/public through an explicit user action and suitable privacy controls.

## Pokémon GO boundary

AR and the GO companion module are DexForge experiences. They do not provide access to undocumented Pokémon GO gameplay/account APIs, location spoofing, automated catches, or automated raids.
