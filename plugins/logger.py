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
    
    # Collection reference
    msg_col = db["messages"]

    # Create TTL index to auto-delete messages older than 48 hours
    async def create_ttl_index():
        try:
            await msg_col.create_index("expire_at", expireAfterSeconds=0)
        except Exception as e:
            logger.warning(f"Could not create TTL index: {e}")

    safe_run(create_ttl_index(), name="CreateMessageTTLIndex")

    @ether.on(events.MessageEdited(incoming=True))
    async def edit_sniffer(event):
        if not event.is_private or event.sender_id == owner_id:
            return
            
        # Fetch original from MongoDB
        cached = await msg_col.find_one({"msg_id": event.id, "chat_id": event.chat_id})
        
        if cached:
            old_text = cached.get('text', "")
            new_text = event.text
            
            if old_text != new_text:
                log_msg = (
                    "<blockquote>"
                    "<b>Message Edited</b>\n"
                    f"<b>User:</b> <a href='tg://user?id={event.sender_id}'>{event.sender_id}</a>\n\n"
                    f"<b>Before:</b>\n<code>{old_text}</code>\n\n"
                    f"<b>After:</b>\n<code>{new_text}</code>"
                    "</blockquote>"
                )
                await ether.send_message("me", log_msg)
        
        # Update MongoDB with new text
        await msg_col.update_one(
            {"msg_id": event.id, "chat_id": event.chat_id},
            {"$set": {"text": event.text, "edit_count": cached.get('edit_count', 0) + 1 if cached else 1}},
            upsert=True
        )

    @ether.on(events.MessageDeleted())
    async def delete_sniffer(event):
        # event.deleted_ids is a list of IDs
        for msg_id in event.deleted_ids:
            # We don't have chat_id in global MessageDeleted, 
            # so we search by msg_id (might have collisions but unlikely in DMs)
            cached = await msg_col.find_one({"msg_id": msg_id})
            
            if cached:
                log_msg = (
                    "<blockquote>"
                    "<b>Message Deleted</b>\n"
                    f"<b>User:</b> <a href='tg://user?id={cached['sender_id']}'>{cached['sender_id']}</a>\n\n"
                    f"<b>Original Content:</b>\n<code>{cached['text']}</code>"
                    "</blockquote>"
                )
                await ether.send_message("me", log_msg)
                
                # Optionally keep in DB but marked as deleted, or just let TTL handle it
                # For now, let's just leave it for the TTL to clean up

    @ether.on(events.NewMessage(incoming=True))
    async def cache_messages(event):
        if not event.is_private or event.sender_id == owner_id:
            return
            
        # Save to MongoDB
        # TTL: 48 hours from now
        expire_at = datetime.utcnow() + timedelta(hours=48)
        
        await msg_col.insert_one({
            "msg_id": event.id,
            "chat_id": event.chat_id,
            "sender_id": event.sender_id,
            "text": event.text,
            "date": datetime.utcnow(),
            "expire_at": expire_at
        })

    logger.info("Message Logger plugin loaded (MongoDB persistence active)")
