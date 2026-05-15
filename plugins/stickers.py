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

logger = get_logger("EtherStickers")

def setup(ether, db, owner_id):

# ============================================
# .kang Command (Sticker Steal)
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.kang(?:\s+(.+))?$", outgoing=True))
    async def kang_handler(event):
        if event.sender_id != owner_id:
            return

        if not event.is_reply:
            await event.edit("<blockquote>Reply to a sticker or image to kang it.</blockquote>")
            return

        reply = await event.get_reply_message()
        user = await ether.get_me()
        
        # Determine emoji
        emoji = event.pattern_match.group(1) or ""
        
        await event.edit("<blockquote><b>Kanging Sticker...</b></blockquote>")

        try:
            # Send the media to 'me' (Saved Messages)
            await ether.send_file(
                "me",
                reply.media,
                caption=f"<blockquote><b>Ether Kang System</b>\n\n<b>Emoji:</b> {emoji}\n<b>Source:</b> {event.chat_id}</blockquote>"
            )
            
            await event.edit(f"<blockquote><b>Media Kanged to Saved Messages!</b>\n\n<b>Emoji:</b> {emoji}</blockquote>")
                
        except Exception as e:
            logger.error(f"Kang error: {e}")
            await event.edit(f"<blockquote>Kang failed: {str(e)}</blockquote>")

# ============================================
# .sticker Command (Image to Sticker)
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.sticker$", outgoing=True))
    async def sticker_handler(event):
        if event.sender_id != owner_id:
            return

        if not event.is_reply:
            await event.edit("<blockquote>Reply to an image to convert to sticker.</blockquote>")
            return

        reply = await event.get_reply_message()
        if not reply.photo and not (reply.document and "image" in reply.document.mime_type):
            await event.edit("<blockquote>Reply to an image file.</blockquote>")
            return

        await event.edit("<blockquote><b>Converting to Sticker...</b></blockquote>")

        try:
            photo = await reply.download_media()
            await ether.send_file(
                event.chat_id,
                photo,
                force_document=False,
                reply_to=event.reply_to_msg_id
            )
            await event.delete()
            os.remove(photo)
        except Exception as e:
            logger.error(f"Sticker convert error: {e}")
            await event.edit(f"<blockquote>Conversion failed: {str(e)}</blockquote>")

# ============================================
# .getsticker Command (Sticker to Image)
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.getsticker$", outgoing=True))
    async def get_sticker_handler(event):
        if event.sender_id != owner_id:
            return

        if not event.is_reply:
            await event.edit("<blockquote>Reply to a sticker to get it as an image.</blockquote>")
            return

        reply = await event.get_reply_message()
        if not reply.sticker:
            await event.edit("<blockquote>Reply to a sticker.</blockquote>")
            return

        await event.edit("<blockquote><b>Extracting Image...</b></blockquote>")

        try:
            image = await reply.download_media()
            await ether.send_file(
                event.chat_id,
                image,
                force_document=True,
                reply_to=event.reply_to_msg_id
            )
            await event.delete()
            os.remove(image)
        except Exception as e:
            logger.error(f"Get sticker error: {e}")
            await event.edit(f"<blockquote>Extraction failed: {str(e)}</blockquote>")

    logger.info("Stickers plugin loaded (.kang, .sticker)")
