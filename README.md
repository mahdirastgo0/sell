# Telegram VPN Sales Bot — FOREIGN VPS edition

This project is intentionally designed to run on a **foreign VPS**. Telegram Bot + backend + PostgreSQL live outside Iran. The backend communicates with the **Iran 3x-ui panel only** through HTTPS and never connects directly to the foreign VPN node.

## Architecture

```text
Telegram user
     |
     v
Foreign VPS
  - Telegram Bot
  - FastAPI health API
  - PostgreSQL
     |
     | HTTPS + Authorization: Bearer <3x-ui API token>
     v
Iran server
  - 3x-ui only
  - panel.kenznum.ir
     |
     +-- inbound 40 -> Local/Direct
     |
     +-- inbound 41 -> tunnel -> Nether remote node
```

This is the intended deployment. **Do not deploy the bot container on the Iran server.**

## Why polling is used

The bot uses Telegram long polling from the foreign VPS. This avoids requiring a public domain/certificate for the bot server. Telegram connections are made from the foreign VPS, while the Iran machine is only the 3x-ui API target.

## Current 3x-ui integration

The code uses the current client-first 3x-ui API:

- Bearer authentication under `/panel/api/*`
- `POST /panel/api/clients/add`
- `GET /panel/api/clients/get/:email`
- `GET /panel/api/clients/traffic/:email`
- `GET /panel/api/clients/links/:email`
- `GET /panel/api/clients/subLinks/:subId`

3x-ui documents Bearer tokens as programmatic authentication and warns that admin tokens are powerful credentials. Keep the token only in `.env` on the foreign VPS.

## Install on the FOREIGN VPS

Requirements: Docker + Docker Compose.

```bash
unzip vpn_bot_foreign.zip
cd vpn_bot
cp .env.example .env
nano .env
chmod 600 .env
docker compose up -d --build
docker compose logs -f app
```

Fill in a **new** Telegram bot token and a **new** 3x-ui API token. The values previously shared in chat should be rotated before production use.

## Network requirements

The foreign VPS needs outbound HTTPS access to:

- `api.telegram.org`
- `panel.kenznum.ir`

The Iran server does not need to receive Telegram traffic from users. The foreign VPS initiates the API connection to the Iran panel.

## First run

Open the Telegram bot and send `/start`.

Admin IDs already configured in `.env.example`:

- `926784487`
- `175030730`

Card payment is configured through `PAYMENT_CARD_NUMBER` and `PAYMENT_CARD_HOLDER`.

## Security

- Never commit `.env`.
- Never put the 3x-ui token in Telegram messages.
- Never send the 3x-ui token to VPN users.
- Use HTTPS for the 3x-ui panel.
- Rotate tokens that have been exposed in chat/logs.
