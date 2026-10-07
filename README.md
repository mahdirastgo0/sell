# Telegram VPN Sales Bot — 3x-ui Iran

Production-oriented Telegram bot for manual card-to-card payments and automatic provisioning through the **Iran 3x-ui panel only**.

## Architecture

Telegram → Python Bot/API → Iran 3x-ui → inbound 40 (direct) / inbound 41 (tunnel → remote node)

The backend never connects directly to the foreign node.

## Features

- User registration
- Editable plans from Telegram admin menu
- Enable/disable/delete plans
- Manual card payment
- Receipt image upload
- Admin approve/reject
- Idempotent provisioning into 3x-ui
- VLESS link retrieval from 3x-ui
- Subscription URL using panel-generated `subId`
- QR code generation
- My services / traffic / expiry
- Renewal flow
- Admin order/service overview
- PostgreSQL persistence
- Docker Compose deployment

## Important security

The bot token and 3x-ui API token previously shared in chat should be rotated. Put the new values only in `.env`; never commit `.env`.

## Install

1. Copy `.env.example` to `.env`.
2. Put a **new** Telegram bot token and a **new** 3x-ui API token in `.env`.
3. Set `PAYMENT_CARD_HOLDER`.
4. Make sure the 3x-ui API token has access to `/panel/api/*`.
5. Run:

```bash
docker compose up -d --build
```

6. Open the bot and send `/start`.

## Notes about 3x-ui

The code uses the current client-first API (`/panel/api/clients/add`, `/panel/api/clients/get/:email`, `/panel/api/clients/subLinks/:subId`) and Bearer-token authentication. It does not call the foreign node directly.
