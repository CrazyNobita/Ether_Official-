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
from datetime import datetime, timedelta
from telethon import events
from utils.logger import get_logger
from utils.task_helper import safe_run

logger = get_logger("MessageLogger")

def setup(ether, db, owner_id):

    msg_col = db["messages"]
    config_col = db["logger_config"]

    # ============================================
    # DEFAULT CONFIG
    # ============================================

    async def get_config():
        cfg = await config_col.find_one({"owner_id": owner_id})
        if not cfg:
            return {
                "enabled": True,
                "log_chat_id": None
            }
        return cfg

    async def set_config(data: dict):
        await config_col.update_one(
            {"owner_id": owner_id},
            {"$set": data},
            upsert=True
        )

    # ============================================
    # TTL INDEX
    # ============================================

    async def create_ttl_index():
        try:
            await msg_col.create_index(
                "expire_at",
                expireAfterSeconds=0
            )
        except Exception as e:
            logger.warning(f"TTL index error: {e}")

    safe_run(create_ttl_index(), name="CreateMessageTTLIndex")

    # ============================================
    # EDIT LOGGER
    # ============================================

    @ether.on(events.MessageEdited(incoming=True))
    async def edit_sniffer(event):

        if event.sender_id == owner_id:
            return

        sender = await event.get_sender()

        # ignore bots / groups / channels
        if (
            not event.is_private
            or not sender
            or getattr(sender, "bot", False)
            or getattr(sender, "broadcast", False)
        ):
            return

        cfg = await get_config()

        if not cfg.get("enabled"):
            return

        log_chat = cfg.get("log_chat_id") or "me"

        cached = await msg_col.find_one({
            "msg_id": event.id,
            "chat_id": event.chat_id
        })

        if cached:
            old_text = cached.get("text", "")
            new_text = event.text or ""

            if old_text != new_text:

                log_msg = (
                    "<blockquote>"
                    "<b>Message Edited</b>\n"
                    f"<b>User:</b> <code>{event.sender_id}</code>\n\n"
                    f"<b>Before:</b>\n<code>{old_text}</code>\n\n"
                    f"<b>After:</b>\n<code>{new_text}</code>"
                    "</blockquote>"
                )

                await ether.send_message(log_chat, log_msg)

        await msg_col.update_one(
            {"msg_id": event.id, "chat_id": event.chat_id},
            {
                "$set": {
                    "text": event.text,
                    "edit_count": cached.get("edit_count", 0) + 1 if cached else 1
                }
            },
            upsert=True
        )

    # ============================================
    # DELETE LOGGER
    # ============================================

    @ether.on(events.MessageDeleted())
    async def delete_sniffer(event):

        cfg = await get_config()

        if not cfg.get("enabled"):
            return

        log_chat = cfg.get("log_chat_id") or "me"

        for msg_id in event.deleted_ids:

            cached = await msg_col.find_one({"msg_id": msg_id})

            if cached:

                log_msg = (
                    "<blockquote>"
                    "<b>Message Deleted</b>\n"
                    f"<b>User:</b> <code>{cached['sender_id']}</code>\n\n"
                    f"<b>Original:</b>\n<code>{cached.get('text', '')}</code>"
                    "</blockquote>"
                )

                await ether.send_message(log_chat, log_msg)

    # ============================================
    # CACHE MESSAGES (PRIVATE ONLY)
    # ============================================

    @ether.on(events.NewMessage(incoming=True))
    async def cache_messages(event):

        if event.sender_id == owner_id:
            return

        sender = await event.get_sender()

        # ignore bots / groups / channels
        if (
            not event.is_private
            or not sender
            or getattr(sender, "bot", False)
            or getattr(sender, "broadcast", False)
        ):
            return

        expire_at = datetime.utcnow() + timedelta(hours=48)

        await msg_col.insert_one({
            "msg_id": event.id,
            "chat_id": event.chat_id,
            "sender_id": event.sender_id,
            "text": event.text,
            "date": datetime.utcnow(),
            "expire_at": expire_at
        })

    # ============================================
    # TOGGLE COMMAND
    # ============================================

    @ether.on(events.NewMessage(pattern=r"^\.log(on|off)$", outgoing=True))
    async def toggle_logger(event):

        if event.sender_id != owner_id:
            return

        mode = event.pattern_match.group(1)

        cfg = await get_config()

        cfg["enabled"] = (mode == "on")

        await set_config(cfg)

        await event.edit(
            f"<blockquote>Logger {'enabled' if mode == 'on' else 'disabled'}.</blockquote>",
            parse_mode="html"
        )

    # ============================================
    # SET LOG CHAT
    # ============================================

    @ether.on(events.NewMessage(pattern=r"^\.setlog$", outgoing=True))
    async def set_log_chat(event):

        if event.sender_id != owner_id:
            return

        chat_id = event.chat_id

        await set_config({
            "log_chat_id": chat_id,
            "enabled": True
        })

        await event.edit(
            "<blockquote>✅ Log chat set successfully.</blockquote>",
            parse_mode="html"
        )
