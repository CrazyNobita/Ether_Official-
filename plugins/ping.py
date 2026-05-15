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

import time
from telethon import events
from utils.logger import get_logger

logger = get_logger("EtherPing")


def setup(ether, db, owner_id):


# ============================================
# Ping Command
# ============================================
    
    @ether.on(events.NewMessage(pattern=r"^\.ping$", outgoing=True))
    async def ping_handler(event):
        start = time.time()

        if event.sender_id != owner_id:
            return
        msg = await event.reply("<blockquote><i>Measuring latency...</i></blockquote>")
        
        latency = int((time.time() - start) * 1000)
        
        await msg.edit(
            f"<blockquote><b>Pong</b> (<code>{latency}ms</code>)</blockquote>"
        )
        
        try:
            await event.delete()
        except Exception:
            pass
    
    logger.info("Ping plugin loaded")
