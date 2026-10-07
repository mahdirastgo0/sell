#!/usr/bin/env bash
set -euo pipefail
cp -n .env.example .env || true
read -r -p 'New Telegram bot token: ' BOT_TOKEN
read -r -s -p 'New 3x-ui API token: ' PANEL_API_TOKEN; echo
read -r -p 'Card number: ' CARD
read -r -p 'Card holder name: ' HOLDER
sed -i "s|PUT_NEW_BOT_TOKEN_HERE|$BOT_TOKEN|" .env
sed -i "s|PUT_NEW_3XUI_API_TOKEN_HERE|$PANEL_API_TOKEN|" .env
sed -i "s|PUT_CARD_NUMBER_HERE|$CARD|" .env
sed -i "s|SET_CARD_HOLDER_NAME|$HOLDER|" .env
chmod 600 .env
docker compose up -d --build
echo 'Bot is starting. Check: docker compose logs -f app'
