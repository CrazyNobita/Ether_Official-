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

from telethon import events, functions, types
from utils.logger import get_logger
import asyncio

logger = get_logger("EtherAdmin")

def setup(ether, db, owner_id):

# ============================================
# .gban Command (Global Ban)
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.gban(?:\s+(.+))?$", outgoing=True))
    async def gban_handler(event):
        if event.sender_id != owner_id:
            return

        target = event.pattern_match.group(1)
        if not target and event.is_reply:
            reply = await event.get_reply_message()
            target = reply.sender_id
        
        if not target:
            await event.edit("<blockquote><b>Command Error:</b> Reply to a user or provide username/ID to GBan.</blockquote>")
            return

        try:
            entity = await ether.get_entity(target)
            user_id = entity.id
            user_name = entity.first_name
        except Exception as e:
            await event.edit(f"<blockquote><b>Identity Error:</b> User not found: {str(e)}</blockquote>")
            return

        if user_id == owner_id:
            await event.edit("<blockquote><b>Validation Error:</b> You cannot GBan yourself!</blockquote>")
            return

        await event.edit(f"<blockquote><b>Initiating Global Ban for {user_name}...</b></blockquote>")

        success_count = 0
        fail_count = 0
        
        async for dialog in ether.iter_dialogs():
            if not (dialog.is_group or dialog.is_channel):
                continue
            
            try:
                await ether(functions.channels.EditBannedRequest(
                    channel=dialog.id,
                    participant=user_id,
                    banned_rights=types.ChatBannedRights(
                        until_date=None,
                        view_messages=True
                    )
                ))
                success_count += 1
                await asyncio.sleep(0.1) # Flood protection
            except Exception:
                fail_count += 1
            
        await event.edit(
            f"<blockquote>"
            f"<b>Global Ban Complete</b>\n\n"
            f"<b>User:</b> {user_name} (<code>{user_id}</code>)\n"
            f"<b>Groups Banned:</b> {success_count}\n"
            f"<b>Failed/No Rights:</b> {fail_count}"
            "</blockquote>"
        )

# ============================================
# .ungban Command
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.ungban(?:\s+(.+))?$", outgoing=True))
    async def ungban_handler(event):
        if event.sender_id != owner_id:
            return

        target = event.pattern_match.group(1)
        if not target and event.is_reply:
            reply = await event.get_reply_message()
            target = reply.sender_id
        
        if not target:
            await event.edit("<blockquote><b>Command Error:</b> Reply to a user or provide username/ID to Un-GBan.</blockquote>")
            return

        try:
            entity = await ether.get_entity(target)
            user_id = entity.id
        except Exception as e:
            await event.edit(f"<blockquote>❌ User not found: {str(e)}</blockquote>")
            return

        await event.edit(f"<blockquote><b>Removing Global Ban...</b></blockquote>")

        success_count = 0
        async for dialog in ether.iter_dialogs():
            if not (dialog.is_group or dialog.is_channel):
                continue

            try:
                await ether(functions.channels.EditBannedRequest(
                    channel=dialog.id,
                    participant=user_id,
                    banned_rights=types.ChatBannedRights(
                        until_date=None,
                        view_messages=False
                    )
                ))
                success_count += 1
                await asyncio.sleep(0.1) # Flood protection
            except Exception:
                pass

        await event.edit(f"<blockquote><b>Global Ban Lifted</b> from {success_count} groups.</blockquote>")

    logger.info("Admin plugin loaded (.gban, .ungban)")
