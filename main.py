# Copyright ©️ 2022 TeLe TiPs. All Rights Reserved
# You are free to use this code in any of your project, but you MUST include the following in your README.md (Copy & paste)
# ##Credits - [Ping All Telegram bot by TeLe TiPs] (https://github.com/teletips/PingAllBot-teletips)
# Changing the code is not allowed! Read GNU AFFERO GENERAL PUBLIC LICENSE: https://github.com/teletips/PingAllBot-teletips/blob/main/LICENSE

from pyrogram import Client, filters
from pyrogram.types import Message
import os
import asyncio
from pyrogram import enums
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait

# Initialize the Telegram client with credentials from environment variables
teletips = Client(
    "ModiMentions",
    api_id=int(os.getenv("API_ID", "22714261")),
    api_hash=os.getenv("API_HASH", "ba5f5b61893c726ff1092caf79425300"),
    bot_token=os.getenv("BOT_TOKEN", "7995762340:AAEyklzw1L3knoPvYUH5_7MWjPbaXEcdcdw")
)

# Global variables for managing chat queue and process control
chatQueue = []
stopProcess = False

@teletips.on_message(filters.command(["awake", "all"]))
async def everyone(client, message):
    """Handle /awake and /all commands to mention all members in the chat"""
    global stopProcess
    
    try:
        # Check if user has admin permissions
        try:
            sender = await teletips.get_chat_member(message.chat.id, message.from_user.id)
            has_permissions = sender.privileges
        except:
            has_permissions = message.sender_chat
        
        if has_permissions:
            # Check if bot is at maximum capacity (5 chats)
            if len(chatQueue) > 5:
                await message.reply("⛔️ | I'm already working on my maximum number of 5 chats at the moment. Please try again shortly.")
            else:
                # Check if there's already a process running in this chat
                if message.chat.id in chatQueue:
                    await message.reply("🚫 | There's already an ongoing process in this chat. Please /stop to start a new one.")
                else:
                    # Add chat to queue
                    chatQueue.append(message.chat.id)
                    
                    # Extract input text from command
                    if len(message.command) > 1:
                        inputText = message.command[1]
                    elif len(message.command) == 1:
                        inputText = ""
                    
                    # Get list of all non-bot, non-deleted members
                    membersList = []
                    try:
                        async for member in teletips.get_chat_members(message.chat.id):
                            if member.user.is_bot == True:
                                pass
                            elif member.user.is_deleted == True:
                                pass
                            else:
                                membersList.append(member.user)
                    except Exception as e:
                        if "CHANNEL_INVALID" in str(e) or "CHAT_ADMIN_REQUIRED" in str(e):
                            await message.reply("🚫 | Unable to access member list. This feature may not be supported in this type of chat or requires additional permissions.")
                            chatQueue.remove(message.chat.id)
                            return
                        else:
                            await message.reply("❌ | An error occurred while fetching members.")
                            chatQueue.remove(message.chat.id)
                            return
                    
                    i = 0
                    lenMembersList = len(membersList)
                    if stopProcess: 
                        stopProcess = False
                    
                    # Mention members in batches of 10
                    while len(membersList) > 0 and not stopProcess:
                        j = 0
                        text1 = f"{inputText}\n\n"
                        
                        try:
                            # Mention up to 10 users per message
                            while j < 10:
                                user = membersList.pop(0)
                                if user.username == None:
                                    text1 += f"{user.mention} "
                                    j += 1
                                else:
                                    text1 += f"@{user.username} "
                                    j += 1
                            
                            try:
                                await teletips.send_message(message.chat.id, text1)
                            except Exception:
                                pass
                            
                            # Wait 10 seconds between messages to avoid flood limits
                            await asyncio.sleep(10)
                            i += 10
                            
                        except IndexError:
                            # Handle last batch with fewer than 10 members
                            try:
                                await teletips.send_message(message.chat.id, text1)
                            except Exception:
                                pass
                            i = i + j
                    
                    # Send completion message
                    if i == lenMembersList:
                        await message.reply(f"✅ | Successfully mentioned **total number of {i} members**.\n❌ | Bots and deleted accounts were rejected.")
                    else:
                        await message.reply(f"✅ | Successfully mentioned **{i} members.**\n❌ | Bots and deleted accounts were rejected.")
                    
                    # Remove chat from queue
                    chatQueue.remove(message.chat.id)
        else:
            await message.reply("👮🏻 | Sorry, **only admins** can execute this command.")
            
    except FloodWait as e:
        await asyncio.sleep(e.value)

@teletips.on_message(filters.command(["remove", "clean"]))
async def remove(client, message):
    """Handle /remove and /clean commands to remove deleted accounts"""
    global stopProcess
    
    try:
        # Check if user has admin permissions
        try:
            sender = await teletips.get_chat_member(message.chat.id, message.from_user.id)
            has_permissions = sender.privileges
        except:
            has_permissions = message.sender_chat
        
        if has_permissions:
            # Check if bot has admin permissions
            bot = await teletips.get_chat_member(message.chat.id, "self")
            if bot.status == ChatMemberStatus.MEMBER:
                await message.reply("🕹 | I need admin permissions to remove deleted accounts.")
            else:
                # Check capacity and queue status
                if len(chatQueue) > 5:
                    await message.reply("⛔️ | I'm already working on my maximum number of 5 chats at the moment. Please try again shortly.")
                else:
                    if message.chat.id in chatQueue:
                        await message.reply("🚫 | There's already an ongoing process in this chat. Please /stop to start a new one.")
                    else:
                        chatQueue.append(message.chat.id)
                        
                        # Find all deleted accounts
                        deletedList = []
                        try:
                            async for member in teletips.get_chat_members(message.chat.id):
                                if member.user.is_deleted == True:
                                    deletedList.append(member.user)
                                else:
                                    pass
                        except Exception as e:
                            if "CHANNEL_INVALID" in str(e) or "CHAT_ADMIN_REQUIRED" in str(e):
                                await message.reply("🚫 | Unable to access member list. This feature may not be supported in this type of chat or requires additional permissions.")
                                chatQueue.remove(message.chat.id)
                                return
                            else:
                                await message.reply("❌ | An error occurred while fetching members.")
                                chatQueue.remove(message.chat.id)
                                return
                        
                        lenDeletedList = len(deletedList)
                        
                        if lenDeletedList == 0:
                            await message.reply("👻 | No deleted accounts in this chat.")
                            chatQueue.remove(message.chat.id)
                        else:
                            k = 0
                            processTime = lenDeletedList * 10
                            temp = await teletips.send_message(message.chat.id, f"🚨 | Total of {lenDeletedList} deleted accounts has been detected.\n⏳ | Estimated time: {processTime} seconds from now.")
                            
                            if stopProcess: 
                                stopProcess = False
                            
                            # Remove deleted accounts one by one
                            while len(deletedList) > 0 and not stopProcess:
                                deletedAccount = deletedList.pop(0)
                                try:
                                    await teletips.ban_chat_member(message.chat.id, deletedAccount.id)
                                except Exception:
                                    pass
                                k += 1
                                await asyncio.sleep(10)
                            
                            # Send completion message
                            if k == lenDeletedList:
                                await message.reply(f"✅ | Successfully removed all deleted accounts from this chat.")
                                await temp.delete()
                            else:
                                await message.reply(f"✅ | Successfully removed {k} deleted accounts from this chat.")
                                await temp.delete()
                            
                            chatQueue.remove(message.chat.id)
        else:
            await message.reply("👮🏻 | Sorry, **only admins** can execute this command.")
            
    except FloodWait as e:
        await asyncio.sleep(e.value)

@teletips.on_message(filters.command(["stop", "cancel"]))
async def stop(client, message):
    """Handle /stop and /cancel commands to halt ongoing processes"""
    global stopProcess
    
    try:
        # Check if user has admin permissions
        try:
            sender = await teletips.get_chat_member(message.chat.id, message.from_user.id)
            has_permissions = sender.privileges
        except:
            has_permissions = message.sender_chat
        
        if has_permissions:
            if not message.chat.id in chatQueue:
                await message.reply("🤷🏻‍♀️ | There is no ongoing process to stop.")
            else:
                stopProcess = True
                await message.reply("🛑 | Stopped.")
        else:
            await message.reply("👮🏻 | Sorry, **only admins** can execute this command.")
            
    except FloodWait as e:
        await asyncio.sleep(e.value)

@teletips.on_message(filters.command(["admins", "staff"]))
async def admins(client, message):
    """Handle /admins and /staff commands to list all administrators"""
    try:
        adminList = []
        ownerList = []
        
        # Get all administrators
        try:
            async for admin in teletips.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
                if admin.privileges.is_anonymous == False:
                    if admin.user.is_bot == True:
                        pass
                    elif admin.status == ChatMemberStatus.OWNER:
                        ownerList.append(admin.user)
                    else:
                        adminList.append(admin.user)
                else:
                    pass
        except Exception as e:
            if "CHANNEL_INVALID" in str(e) or "CHAT_ADMIN_REQUIRED" in str(e):
                await message.reply("🚫 | Unable to fetch admin list from this chat. This feature may not be supported in this type of chat or requires additional permissions.")
                return
            else:
                await message.reply("❌ | An error occurred while fetching administrators.")
                return
        
        lenAdminList = len(ownerList) + len(adminList)
        text2 = f"**GROUP STAFF - {message.chat.title}**\n\n"
        
        # Display owner
        try:
            owner = ownerList[0]
            if owner.username == None:
                text2 += f"👑 Owner\n└ {owner.mention}\n\n👮🏻 Admins\n"
            else:
                text2 += f"👑 Owner\n└ @{owner.username}\n\n👮🏻 Admins\n"
        except:
            text2 += f"👑 Owner\n└ <i>Hidden</i>\n\n👮🏻 Admins\n"
        
        # Display admins
        if len(adminList) == 0:
            text2 += "└ <i>Admins are hidden</i>"
            await teletips.send_message(message.chat.id, text2)
        else:
            while len(adminList) > 1:
                admin = adminList.pop(0)
                if admin.username == None:
                    text2 += f"├ {admin.mention}\n"
                else:
                    text2 += f"├ @{admin.username}\n"
            else:
                admin = adminList.pop(0)
                if admin.username == None:
                    text2 += f"└ {admin.mention}\n\n"
                else:
                    text2 += f"└ @{admin.username}\n\n"
            
            text2 += f"✅ | **Total number of admins**: {lenAdminList}\n❌ | Bots and hidden admins were rejected."
            await teletips.send_message(message.chat.id, text2)
            
    except FloodWait as e:
        await asyncio.sleep(e.value)

@teletips.on_message(filters.command("bots"))
async def bots(client, message):
    """Handle /bots command to list all bots in the chat"""
    try:
        botList = []
        
        try:
            # Get all bots
            async for bot in teletips.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.BOTS):
                botList.append(bot.user)
        except Exception as e:
            # Handle cases where bot listing is not supported (e.g., certain channels)
            if "CHANNEL_INVALID" in str(e) or "CHAT_ADMIN_REQUIRED" in str(e):
                await message.reply("🚫 | Unable to fetch bot list from this chat. This feature may not be supported in this type of chat or requires additional permissions.")
                return
            else:
                await message.reply("❌ | An error occurred while fetching the bot list.")
                return
        
        if len(botList) == 0:
            await message.reply("🤖 | No bots found in this chat.")
            return
        
        lenBotList = len(botList)
        text3 = f"**BOT LIST - {message.chat.title}**\n\n🤖 Bots\n"
        
        # Display bots
        while len(botList) > 1:
            bot = botList.pop(0)
            text3 += f"├ @{bot.username}\n"
        else:
            bot = botList.pop(0)
            text3 += f"└ @{bot.username}\n\n"
        
        text3 += f"✅ | **Total number of bots**: {lenBotList}"
        await teletips.send_message(message.chat.id, text3)
        
    except FloodWait as e:
        await asyncio.sleep(e.value)

@teletips.on_message(filters.command("start") & filters.private)
async def start(client, message):
    """Handle /start command in private messages"""
    text = f'''
Heya {message.from_user.mention},

My name is **𝐌𝐎𝐃𝐈 𝐌𝐄𝐍𝐓𝐈𝐎𝐍 𝐁𝐎𝐓**. I'm here to help you to get everyone's attention by mentioning all members in your chat.

I have some additional cool features and also I can work in channels.

**Creator**: 𝐍𝐀गे𝐒𝐇व𝐑 (@Bhosade)

[Join our community](https://t.me/Realm_Of_Anime) for anime discussions and updates!

Hit /help to find out my commands and the use of them.
'''
    try:
        # Send the image with the welcome message
        await teletips.send_photo(message.chat.id, "modi_bot_image.jpeg", caption=text, disable_notification=True)
    except Exception:
        # Fallback to text message if image fails
        await teletips.send_message(message.chat.id, text, disable_web_page_preview=True)

@teletips.on_message(filters.command("help"))
async def help(client, message):
    """Handle /help command to show available commands"""
    text = '''
Hey, let's have a quick look at my commands.

**𝐌𝐎𝐃𝐈 𝐌𝐄𝐍𝐓𝐈𝐎𝐍 𝐁𝐎𝐓 Commands**:

- /awake "input": <i>Mention all members.</i>

- /remove: <i>Remove all deleted accounts.</i>

- /admins: <i>Mention all admins.</i>

- /bots: <i>Get the full bot list.</i>

- /stop: <i>Stop an on going process.</i>

**Creator**: 𝐍𝐀गे𝐒𝐇व𝐑 (@Bhosade)

[Join our community](https://t.me/Realm_Of_Anime) for more awesome bots and discussions!
'''
    await teletips.send_message(message.chat.id, text, disable_web_page_preview=True)

# Main execution
if __name__ == "__main__":
    print("🚀 𝐌𝐎𝐃𝐈 𝐌𝐄𝐍𝐓𝐈𝐎𝐍 𝐁𝐎𝐓 is starting...")
    print("📡 Connecting to Telegram...")
    
    try:
        print("✅ 𝐌𝐎𝐃𝐈 𝐌𝐄𝐍𝐓𝐈𝐎𝐍 𝐁𝐎𝐓 is alive and running!")
        teletips.run()
    except Exception as e:
        print(f"❌ Error starting bot: {e}")

# Copyright ©️ 2022 TeLe TiPs. All Rights Reserved
