# Ubuntu 24.04 Fix + Deployment Guide (Pyrogram Bot)

Use this when you get errors like:
- `.venv/bin/activate: No such file or directory`
- `python3.12-venv` missing
- broken virtual environment

## 1) Install required packages
```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3-pip
```

## 2) Recreate virtual environment (clean fix)
```bash
cd /opt/june-hosting-bot
rm -rf .venv
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r bot_requirements.txt
```

## 3) Configure environment
Create `.env` in project root (`/opt/june-hosting-bot/.env`):
```env
API_ID=36371827
API_HASH=4b33c6649f49006c2954c1635e448574
BOT_TOKEN=8269981439:AAHawY-6QKlG6DxgUw1SwlDBZHo-XZyEWxY
OWNER_IDS=8780206093
ADMIN_IDS=8780206093,7363967303
DEFAULT_PLAN=free
PLAN_FREE_LIMIT=1
PLAN_PLUS_LIMIT=3
PLAN_PRO_LIMIT=6
MAX_RAM_MB=1024
```

## 4) Use safe starter script
`start.sh` in repo root safely loads `.env` only if it exists and runs `.venv/bin/python main.py`.

Run once manually:
```bash
cd /opt/june-hosting-bot
./start.sh
```

## 5) Install/refresh systemd service
Copy service file:
```bash
sudo cp june-hosting-bot.service /etc/systemd/system/june-hosting-bot.service
sudo systemctl daemon-reload
sudo systemctl enable june-hosting-bot
sudo systemctl restart june-hosting-bot
```

## 6) Verify service health
```bash
systemctl status june-hosting-bot --no-pager
```
Expected:
- `Active: active (running)`

If failing, print logs:
```bash
journalctl -u june-hosting-bot -n 120 --no-pager
```

## 7) Quick recovery command set
```bash
cd /opt/june-hosting-bot \
&& sudo apt update \
&& sudo apt install -y python3.12 python3.12-venv python3-pip \
&& rm -rf .venv \
&& python3.12 -m venv .venv \
&& source .venv/bin/activate \
&& python -m pip install --upgrade pip \
&& pip install -r bot_requirements.txt \
&& sudo systemctl daemon-reload \
&& sudo systemctl restart june-hosting-bot \
&& systemctl status june-hosting-bot --no-pager
```
