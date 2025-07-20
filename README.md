# 𝐌𝐎𝐃𝐈 𝐌𝐄𝐍𝐓𝐈𝐎𝐍 𝐁𝐎𝐓 - TeLeTiPs

Powerful Telegram bot to get everyone's attention by mentioning all members in the chat. 𝐌𝐎𝐃𝐈 𝐌𝐄𝐍𝐓𝐈𝐎𝐍 𝐁𝐎𝐓 has some additional cool features and also it can work in channels. It's easy, fast and self deployable.

## 🚀 Deployed on Replit

This bot is configured to run on Replit with the following features:

### 📄 Commands

- **🛎 /awake, /all** - To get everyone's attention by mentioning all members in the chat
- **👻 /remove, /clean** - To remove all deleted accounts from the chat
- **👮🏻 /admins, /staff** - To mention all admins while getting the full non-anonymous admin list
- **👾 /bots** - To get the full bot list of the chat
- **🛑 /stop, /cancel** - To stop an ongoing process in the chat

### ⚒ Configuration

The bot uses environment variables for configuration:

- `API_ID`: Telegram API ID (from my.telegram.org/apps)
- `API_HASH`: Telegram API Hash (from my.telegram.org/apps)
- `BOT_TOKEN`: Bot Token (from @BotFather)

### 🔧 Setup on Replit

1. Fork this repository to your Replit account
2. Set up the environment variables in Replit's Secrets tab:
   - API_ID: 22714261
   - API_HASH: ba5f5b61893c726ff1092caf79425300
   - BOT_TOKEN: 7995762340:AAEyklzw1L3knoPvYUH5_7MWjPbaXEcdcdw
3. Run the bot using the "Run" button

### 📱 Features

- **Queue Management**: Handles up to 5 concurrent chats
- **Flood Protection**: Built-in rate limiting and flood wait handling
- **Admin Permissions**: Checks for proper admin permissions before executing commands
- **Error Handling**: Comprehensive error handling for all operations
- **Process Control**: Ability to stop ongoing operations
- **Works in Groups and Channels**: Full compatibility with both group chats and channels

### 🛡 Permissions Required

For full functionality, the bot needs:
- Admin permissions in the chat (for /remove command)
- Ability to read messages and member lists
- Ability to send messages and mention users

### ⚡ Dependencies

- `pyrogram`: Modern, elegant and asynchronous Telegram MTProto API framework
- `tgcrypto`: Fast cryptographic library for pyrogram

### 📞 Support & Community

- Community: [Realm Of Anime](https://t.me/Realm_Of_Anime)
- Creator: 𝐍𝐀गे𝐒𝐇व𝐑 (@Bhosade)

## Credits

- Original base: [Ping All Bot by TeLe TiPs](https://github.com/teletips/PingAllBot-TeLeTiPs)
- Customized by: 𝐍𝐀गे𝐒𝐇व𝐑 (@Bhosade)

## ⚖️ License

This project is licensed under the GNU Affero General Public License v3.0

Copyright ©️ 2022 TeLe TiPs. All Rights Reserved

---

*Note: This bot is configured specifically for Replit deployment with the provided credentials.*
