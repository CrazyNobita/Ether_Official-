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
import time
from utils.logger import get_logger

logger = get_logger("EtherAFK")

# AFK State
AFK_STATE = {
    "is_afk": False,
    "reason": "",
    "time": 0
}

def setup(ether, db, owner_id):

# ============================================
# .afk Command
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.afk(?:\s+(.+))?$", outgoing=True))
    async def set_afk_handler(event):
        if event.sender_id != owner_id:
            return

        reason = event.pattern_match.group(1) or "I'm currently away."
        AFK_STATE["is_afk"] = True
        AFK_STATE["reason"] = reason
        AFK_STATE["time"] = time.time()

        await event.edit(f"<blockquote><b>I'm now AFK</b>\n\n<b>Reason:</b> {reason}</blockquote>")

# ============================================
# .status Command (Check AFK status)
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.status$", outgoing=True))
    async def afk_status_handler(event):
        if event.sender_id != owner_id:
            return

        if not AFK_STATE["is_afk"]:
            await event.edit("<blockquote><b>Status:</b> Active (Not AFK)</blockquote>")
            return

        uptime = int(time.time() - AFK_STATE["time"])
        h = uptime // 3600
        m = (uptime % 3600) // 60
        s = uptime % 60
        duration = f"{h}h {m}m {s}s" if h > 0 else (f"{m}m {s}s" if m > 0 else f"{s}s")

        await event.edit(
            f"<blockquote>"
            f"<b>Status: AFK</b>\n"
            f"<b>Reason:</b> {AFK_STATE['reason']}\n"
            f"<b>Duration:</b> {duration}"
            "</blockquote>"
        )

# ============================================
# AFK Watcher (Disable AFK)
# ============================================

    @ether.on(events.NewMessage(outgoing=True))
    async def disable_afk_handler(event):
        if not AFK_STATE["is_afk"]:
            return

        # Don't disable if it's the .afk command or .status/other check commands
        if event.text.startswith(".afk") or event.text.startswith(".status"):
            return

        AFK_STATE["is_afk"] = False
        uptime = int(time.time() - AFK_STATE["time"])
        
        # Convert seconds to readable format for the log
        h = uptime // 3600
        m = (uptime % 3600) // 60
        s = uptime % 60
        duration = f"{h}h {m}m {s}s" if h > 0 else (f"{m}m {s}s" if m > 0 else f"{s}s")


# ============================================
# Mention/DM Watcher
# ============================================

    @ether.on(events.NewMessage(incoming=True))
    async def afk_reply_handler(event):
        if not AFK_STATE["is_afk"]:
            return

        # Reply if it's a DM or a mention in a group
        if event.is_private or event.mentioned:
            # Avoid infinite loops or replying to bots
            try:
                sender = await event.get_sender()
                if not sender or sender.bot or event.sender_id == owner_id:
                    return
            except:
                return

            uptime = int(time.time() - AFK_STATE["time"])
            h = uptime // 3600
            m = (uptime % 3600) // 60
            s = uptime % 60
            duration = f"{h}h {m}m {s}s" if h > 0 else (f"{m}m {s}s" if m > 0 else f"{s}s")

            reply_text = (
                "<blockquote>"
                "<b>User is AFK</b>\n\n"
                f"<b>Reason:</b> {AFK_STATE['reason']}\n"
                f"<b>Since:</b> {duration} ago"
                "</blockquote>"
            )
            
            await event.reply(reply_text)

