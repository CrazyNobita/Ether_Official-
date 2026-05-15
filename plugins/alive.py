# =============================================================================
#  Ether Userbot System
#
#  Project Name:  Ether
#  Author:        LearningBotsOfficial
#
#  Repository:    https://github.com/LearningBotsOfficial/Ether
#
#  Support:       https://t.me/Ether_Support
#  Channel:       https://t.me/Ether_Update
#
#  License:       Open Source (Keep Credits)
#
#  IMPORTANT:
#    • If you copy, fork, or reuse this project or any part of it,
#      you MUST retain original credits.
#    • Proper attribution to Ether project is required.
#
#  Thank you for respecting open-source development.
# =============================================================================

import asyncio
import time
import psutil
import platform
import sys
import os
from datetime import datetime
from telethon import events, Button
from config.config import Config
from utils.logger import get_logger

# START_TIME is accessed via Config.START_TIME

logger = get_logger("EtherAlive")


def setup(ether, db, owner_id):
    ALIVE_IMAGE = "assets/ether_logo.png"

    @ether.on(events.NewMessage(pattern=r"^\.alive$", outgoing=True))
    async def alive_handler(event):
        if event.sender_id != owner_id:
            return

        bot_username = Config.BOT_USERNAME
        if not bot_username:
            await event.reply("<blockquote><b>Identity Error:</b> BOT_USERNAME not fetched yet. Please wait.</blockquote>")
            return

        try:
            await event.delete()
            
            # Calculate Uptime
            uptime_seconds = int(time.time() - Config.START_TIME)
            days, remainder = divmod(uptime_seconds, 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            uptime = f"{days}d {hours}h {minutes}m {seconds}s"
            
            # System Stats
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            
            bot_info = Config.BOT_MENTION or "Bot"
            
            results = await ether.inline_query(bot_username, "alive")
            
            if results:
                await results[0].click(event.chat_id)
            else:
                # Fallback if inline query results are empty
                await event.respond(
                    "<blockquote>"
                    "<b>Ether System Status</b>\n\n"
                    f"<b>Bot:</b> {bot_info}\n"
                    "<b>Status:</b> ONLINE\n"
                    f"<b>Uptime:</b> {uptime}\n"
                    f"<b>CPU:</b> {cpu}%\n"
                    f"<b>RAM:</b> {ram}%\n"
                    f"<b>Disk:</b> {disk}%"
                    "</blockquote>",
                )

        except Exception as e:
            logger.error(f"Alive error: {e}")
            await event.respond("<blockquote><b>Error:</b> Alive signal failed.</blockquote>")

    @ether.on(events.NewMessage(pattern=r"^\.restart$", outgoing=True))
    async def restart_handler(event):
        if event.sender_id != owner_id:
            return
            
        await event.edit("<blockquote><b>Restarting Ether...</b>\n<i>System reboot in progress.</i></blockquote>")
        
        # Give it a moment to send the message
        await asyncio.sleep(2)
        
        logger.info("Restarting bot via .restart command")
        os.execv(sys.executable, [sys.executable] + sys.argv)
