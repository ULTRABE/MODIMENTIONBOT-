# 𝐌𝐎𝐃𝐈 𝐌𝐄𝐍𝐓𝐈𝐎𝐍 𝐁𝐎𝐓 - Deployment Guide

## Quick Setup for Any Platform

### Files Included:
- `main.py` - Main bot script
- `modi_bot_image.jpeg` - Welcome image
- `bot_requirements.txt` - Python dependencies
- `.env.example` - Environment variables template
- `README.md` - Full documentation
- `DEPLOYMENT_GUIDE.md` - This guide

### Environment Variables:
```
API_ID=22714261
API_HASH=ba5f5b61893c726ff1092caf79425300
BOT_TOKEN=7995762340:AAEyklzw1L3knoPvYUH5_7MWjPbaXEcdcdw
```

### Dependencies:
```bash
pip install pyrogram tgcrypto
```

### Run Command:
```bash
python main.py
```

## Platform-Specific Deployment:

### 1. Heroku
1. Create new app on Heroku
2. Connect to GitHub or upload files
3. Add environment variables in Settings > Config Vars
4. Deploy from main branch

### 2. Railway
1. Create new project
2. Deploy from GitHub or upload files
3. Add environment variables in Variables tab
4. Auto-deploy enabled

### 3. Render
1. Create new Web Service
2. Connect repository or upload
3. Add environment variables
4. Build command: `pip install -r bot_requirements.txt`
5. Start command: `python main.py`

### 4. PythonAnywhere
1. Upload files to your account
2. Create new console
3. Install dependencies: `pip3.10 install --user pyrogram tgcrypto`
4. Run: `python3.10 main.py`

### 5. VPS/Server
1. Upload files to server
2. Install Python 3.7+
3. Install dependencies: `pip install -r bot_requirements.txt`
4. Run: `python main.py`
5. Use screen/tmux for background: `screen -S bot python main.py`

## Bot Commands:
- `/awake` or `/all` - Mention all members
- `/remove` or `/clean` - Remove deleted accounts
- `/admins` or `/staff` - List administrators
- `/bots` - Show all bots
- `/stop` or `/cancel` - Stop ongoing process
- `/start` - Welcome message with image
- `/help` - Show commands

## Creator:
- Name: 𝐍𝐀गے𝐒𝐇व𝐑
- Username: @Bhosade
- Community: https://t.me/Realm_Of_Anime

## Important Notes:
1. Bot needs admin permissions in groups for full functionality
2. `/remove` command requires bot to have admin rights
3. Custom image will show with welcome message
4. Works in both groups and channels
5. Has built-in flood protection and queue management

Enjoy your 𝐌𝐎𝐃𝐈 𝐌𝐄𝐍𝐓𝐈𝐎𝐍 𝐁𝐎𝐓! 🚀