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

from telethon import events
import asyncio
import aiohttp
import re
from utils.logger import get_logger

logger = get_logger("EtherUtils")

def setup(ether, db, owner_id):

# ============================================
# .sd (Self-Destruct) Command
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.sd\s+(\d+)\s+(.+)$", outgoing=True))
    async def self_destruct_handler(event):
        if event.sender_id != owner_id:
            return

        seconds = int(event.pattern_match.group(1))
        content = event.pattern_match.group(2)

        if seconds < 1 or seconds > 3600:
            await event.edit("<blockquote><b>Validation Error:</b> Time must be between 1 and 3600 seconds.</blockquote>")
            return

        await event.edit(f"<blockquote>{content}\n\n<i>This message will self-destruct in {seconds} seconds...</i></blockquote>")
        
        await asyncio.sleep(seconds)
        try:
            await event.delete()
        except Exception:
            pass

# ============================================
# .tr (Translator) Command
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.tr\s+([a-z]{2})(?:\s+(.+))?$", outgoing=True))
    async def translate_handler(event):
        if event.sender_id != owner_id:
            return

        lang = event.pattern_match.group(1)
        text = event.pattern_match.group(2)

        if not text and event.is_reply:
            reply = await event.get_reply_message()
            text = reply.text
        
        if not text:
            await event.edit("<blockquote><b>Command Error:</b> Provide text or reply to a message to translate.</blockquote>")
            return

        await event.edit("<blockquote><b>Translating...</b></blockquote>")

        try:
            # Using a public translation API (MyMemory)
            url = f"https://api.mymemory.translated.net/get?q={text}&langpair=auto|{lang}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
                    translated_text = data['responseData']['translatedText']
                    
            await event.edit(
                f"<blockquote>"
                f"<b>Original:</b>\n<i>{text}</i>\n\n"
                f"<b>Translated ({lang}):</b>\n<i>{translated_text}</i>"
                f"</blockquote>"
            )
        except Exception as e:
            logger.error(f"Translation error: {e}")
            await event.edit(f"<blockquote><b>System Error:</b> Translation failed: {str(e)}</blockquote>")

    logger.info("Utility plugin loaded (.sd, .tr)")
