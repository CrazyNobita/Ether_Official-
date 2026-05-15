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
import os

logger = get_logger("EtherInfo")

def setup(ether, db, owner_id):

# ============================================
# .id Command
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.id(?:\s+(.+))?$", outgoing=True))
    async def id_handler(event):
        if event.sender_id != owner_id:
            return

        target = event.pattern_match.group(1)
        
        text = "<blockquote><b>Identity Info</b>\n\n"
        
        # 1. Chat Info
        text += f"<b>Chat ID:</b> <code>{event.chat_id}</code>\n"
        
        # 2. Reply Info
        if event.is_reply:
            reply = await event.get_reply_message()
            sender_id = reply.sender_id
            text += f"<b>Replied User:</b> <code>{sender_id}</code>\n"
            text += f"<b>Message ID:</b> <code>{reply.id}</code>\n"
            
            # If forwarded
            if reply.forward:
                fwd = reply.forward
                if fwd.sender_id:
                    text += f"<b>Forwarded From:</b> <code>{fwd.sender_id}</code>\n"
        
        # 3. Targeted Entity Info
        elif target:
            try:
                entity = await ether.get_entity(target)
                text += f"<b>Target ID:</b> <code>{entity.id}</code>\n"
                text += f"<b>Type:</b> {type(entity).__name__}\n"
            except Exception as e:
                text += f"<b>Error:</b> {str(e)}\n"
        
        # 4. Self Info (if no reply/target)
        else:
            text += f"<b>Your ID:</b> <code>{event.sender_id}</code>\n"

        text += "</blockquote>"
        await event.edit(text)

# ============================================
# .info Command
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.info(?:\s+(.+))?$", outgoing=True))
    async def info_handler(event):
        if event.sender_id != owner_id:
            return

        target = event.pattern_match.group(1)
        await event.edit("<blockquote><b>Analyzing Entity...</b></blockquote>")
        
        try:
            # Determine Entity
            if event.is_reply:
                reply_msg = await event.get_reply_message()
                # Use from_id if possible (handles channels better)
                entity_id = reply_msg.sender_id or reply_msg.peer_id
                entity = await ether.get_entity(entity_id)
            elif target:
                entity = await ether.get_entity(target)
            else:
                entity = await ether.get_me()

            # --- HANDLE USERS ---
            if isinstance(entity, types.User):
                full = await ether(functions.users.GetFullUserRequest(id=entity.id))
                details = {
                    "Type": "User",
                    "Name": f"{entity.first_name} {entity.last_name or ''}",
                    "ID": entity.id,
                    "Username": f"@{entity.username}" if entity.username else "None",
                    "DC ID": entity.photo.dc_id if entity.photo else "N/A",
                    "Bot": "Yes" if entity.bot else "No",
                    "Premium": "Yes" if getattr(entity, 'premium', False) else "No",
                    "Bio": full.full_user.about or "No Bio"
                }

            # --- HANDLE CHANNELS / MEGAGROUPS ---
            elif isinstance(entity, types.Channel):
                full = await ether(functions.channels.GetFullChannelRequest(channel=entity))
                details = {
                    "Type": "Channel" if entity.broadcast else "Megagroup",
                    "Title": entity.title,
                    "ID": entity.id,
                    "Username": f"@{entity.username}" if entity.username else "None",
                    "Members": full.full_user.participants_count or "N/A",
                    "DC ID": entity.photo.dc_id if entity.photo else "N/A",
                    "Description": full.full_user.about or "No Description",
                    "Restricted": "Yes" if entity.restricted else "No"
                }

            # --- HANDLE BASIC CHATS (OLD GROUPS) ---
            elif isinstance(entity, types.Chat):
                full = await ether(functions.messages.GetFullChatRequest(chat_id=entity.id))
                details = {
                    "Type": "Group (Basic)",
                    "Title": entity.title,
                    "ID": entity.id,
                    "Members": entity.participants_count,
                    "Description": "Basic Telegram group"
                }
            else:
                await event.edit(f"<blockquote><b>Error:</b> Unknown entity type: {type(entity).__name__}</blockquote>")
                return

            # Format text
            info_text = "<blockquote>"
            info_text += f"<b>{details.get('Type', 'Entity')} Info</b>\n\n"
            for k, v in details.items():
                if k not in ["Type", "Bio", "Description"]:
                    info_text += f"<b>{k}:</b> <code>{v}</code>\n"
            
            # Add multiline content at end
            desc_label = "Bio" if "Bio" in details else "Description"
            info_text += f"\n<b>{desc_label}:</b>\n<i>{details.get(desc_label)}</i>"
            info_text += "</blockquote>"

            # Profile photo handling
            photo = await ether.download_profile_photo(entity.id, file="temp_pfp.jpg")
            if photo:
                await ether.send_file(event.chat_id, photo, caption=info_text, reply_to=event.reply_to_msg_id)
                await event.delete()
                os.remove(photo)
            else:
                await event.edit(info_text)

        except Exception as e:
            logger.error(f"Info error: {e}")
            await event.edit(f"<blockquote>Failed to fetch info: {str(e)}</blockquote>")

    logger.info("Enhanced Info plugin loaded")
