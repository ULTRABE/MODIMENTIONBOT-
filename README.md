# Private Telegram Hosting Bot (Single-File Python/Node)

This bot lets users upload a single `.py` or `.js` file from Telegram and host it directly on your VPS.

## Core Features
- ♾️ Free 24/7 hosting style flow (runs on your own VPS uptime)
- 🔁 Auto-start after upload + restart/stop controls
- 📜 Live logs + status check for each uploaded file
- 🔒 Private owner/admin controls with plan limits
- ⚡ Fast deployment on Linux VPS (Hostinger KVM supported)

## Start Screen UX
`/start` replies with:
- user ID
- user plan
- uploaded file count / plan limit
- inline button menu:
  - Updates Channel
  - Upload File
  - Check Files
  - Bot Speed
  - Statistics
  - Contact Owner
  - Manual Install
  - Help

## Commands
- `/start`
- `/myfiles` (or `/files`) to list/manage uploaded files
- `/setplan <user_id> <free|plus|pro>` admin only

## Environment Variables
```env
API_ID=YOUR_API_ID
API_HASH=YOUR_API_HASH
BOT_TOKEN=YOUR_BOT_TOKEN
OWNER_IDS=123456789
ADMIN_IDS=123456789
DEFAULT_PLAN=free
PLAN_FREE_LIMIT=1
PLAN_PLUS_LIMIT=3
PLAN_PRO_LIMIT=6
MAX_RAM_MB=1024
```

## Install
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r bot_requirements.txt
python3 main.py
```

## Notes
- Node files use memory cap: `--max-old-space-size=MAX_RAM_MB`.
- If upload start fails, bot returns startup logs in chat and rejects the upload.
- Uploaded files are stored in `data/uploads`, logs in `data/logs`, metadata in `data/state.json`.
