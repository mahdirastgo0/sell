#!/usr/bin/env bash
set -euo pipefail

if ! command -v docker >/dev/null 2>&1; then
  echo 'Docker is required. Install Docker on the FOREIGN VPS first.'
  exit 1
fi

cp -n .env.example .env || true
chmod 600 .env

python3 - <<'PY'
from pathlib import Path
p=Path('.env')
s=p.read_text()
for key, marker in [('BOT_TOKEN','PUT_NEW_BOT_TOKEN_HERE'),('PANEL_API_TOKEN','PUT_NEW_3XUI_API_TOKEN_HERE'),('PAYMENT_CARD_NUMBER','PUT_CARD_NUMBER_HERE')]:
    if marker in s:
        value=input(f'{key}: ') if key!='PANEL_API_TOKEN' else __import__('getpass').getpass(f'{key}: ')
        s=s.replace(marker,value,1)
holder=input('PAYMENT_CARD_HOLDER (optional): ')
s=s.replace('PUT_CARD_HOLDER_NAME_HERE',holder,1)
import secrets
s=s.replace('CHANGE_THIS_LONG_RANDOM_PASSWORD',secrets.token_urlsafe(32),1)
p.write_text(s)
PY

docker compose up -d --build
echo
echo 'Foreign VPS bot started.'
echo 'Logs: docker compose logs -f app'
