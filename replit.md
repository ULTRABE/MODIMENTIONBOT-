# 𝐌𝐎𝐃𝐈 𝐌𝐄𝐍𝐓𝐈𝐎𝐍 𝐁𝐎𝐓 - TeLeTiPs

## Overview

This is a Telegram bot built with Pyrogram that enables users to mention all members in a chat, along with additional administrative features. The bot has been customized and rebranded as "𝐌𝐎𝐃𝐈 𝐌𝐄𝐍𝐓𝐈𝐎𝐍 𝐁𝐎𝐓" and is designed to work in both group chats and channels, with built-in queue management and flood protection.

## User Preferences

Preferred communication style: Simple, everyday language.
Bot customization: Rebranded to "𝐌𝐎𝐃𝐈 𝐌𝐄𝐍𝐓𝐈𝐎𝐍 𝐁𝐎𝐓" with custom welcome image integration.
Command customization: Changed primary mention command from /ping to /awake.
Creator information: 𝐍𝐀गे𝐒𝐇व𝐑 (@Bhosade, User ID: 7831822081)
Community channel: https://t.me/Realm_Of_Anime

## System Architecture

### Core Framework
- **Pyrogram**: Python Telegram client library for building the bot
- **Asynchronous Programming**: Uses async/await patterns for handling concurrent operations
- **Environment-based Configuration**: Configuration through environment variables for security

### Bot Architecture
- **Event-driven Design**: Command handlers respond to specific Telegram messages
- **Queue Management System**: Manages concurrent chat operations with a maximum of 5 simultaneous chats
- **Permission-based Access Control**: Validates admin permissions before executing sensitive commands

## Key Components

### 1. Bot Client (`teletips`)
- Initializes Pyrogram client with API credentials
- Handles connection to Telegram servers
- Manages bot session and authentication

### 2. Command Handlers
- **Awake Commands** (`/awake`, `/all`): Main functionality for mentioning all chat members
- **Cleanup Commands** (`/remove`, `/clean`): Remove deleted accounts from chat
- **Admin Commands** (`/admins`, `/staff`): Mention all administrators
- **Utility Commands** (`/bots`, `/stop`, `/cancel`): Additional chat management features

### 3. Queue Management
- **Global Chat Queue**: Tracks active operations across multiple chats
- **Concurrency Limiting**: Maximum 5 concurrent chat operations
- **Process Control**: Global stop mechanism for interrupting operations

### 4. Permission System
- **Admin Verification**: Checks user admin status before command execution
- **Privilege Validation**: Ensures bot has necessary permissions
- **Sender Chat Support**: Handles both user and channel message sending

## Data Flow

1. **Command Reception**: Bot receives command message from Telegram
2. **Permission Check**: Validates sender's admin permissions
3. **Queue Management**: Checks capacity and existing processes
4. **Operation Execution**: Performs requested action (member listing, cleanup, etc.)
5. **Error Handling**: Manages flood limits and API errors
6. **Response**: Sends appropriate feedback to chat

## External Dependencies

### Telegram API Integration
- **API Credentials**: Requires API_ID and API_HASH from my.telegram.org
- **Bot Token**: Bot token from @BotFather
- **Pyrogram Library**: Python client for Telegram Bot API

### Runtime Dependencies
- **Python Environment**: Asynchronous Python runtime
- **Environment Variables**: Secure configuration storage
- **Network Access**: Stable internet connection for Telegram API calls

## Deployment Strategy

### Replit Platform
- **Environment Configuration**: Uses Replit's Secrets tab for sensitive credentials
- **One-click Deployment**: Simple fork and run setup
- **Persistent Runtime**: Maintains bot session across restarts

### Configuration Requirements
- Set `API_ID`, `API_HASH`, and `BOT_TOKEN` in environment variables
- Ensure bot has admin permissions in target chats
- Grant necessary permissions for member access and message sending

### Security Considerations
- Credentials stored as environment variables
- Permission validation before sensitive operations
- Rate limiting through queue management
- Flood wait handling for API compliance

### Scalability Features
- Queue-based concurrency control
- Process interruption capabilities
- Error recovery mechanisms
- Multi-chat support with resource management