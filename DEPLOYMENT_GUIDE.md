# Deployment Guide (Hostinger KVM VPS)

## 1) System packages
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nodejs npm
```

## 2) Upload bot files
Upload repository contents to your VPS, then:
```bash
cd /path/to/repo
python3 -m venv .venv
source .venv/bin/activate
pip install -r bot_requirements.txt
```

## 3) Set environment variables
```bash
export API_ID="YOUR_API_ID"
export API_HASH="YOUR_API_HASH"
export BOT_TOKEN="YOUR_BOT_TOKEN"
export OWNER_IDS="123456789"
export ADMIN_IDS="123456789"
export MAX_RAM_MB="1024"
```

## 4) Start bot
```bash
source .venv/bin/activate
python3 main.py
```

## 5) Production (recommended)
Use `systemd` for auto-restart and uptime:
- service restart on crash
- boot start
- log persistence

## Capacity target
For 5-8 hosted single-file bots on 2 vCPU / 8GB RAM:
- keep `MAX_RAM_MB` around 512-1024 per Node process
- monitor with `htop`/`ps`
- avoid CPU-heavy scripts in parallel
