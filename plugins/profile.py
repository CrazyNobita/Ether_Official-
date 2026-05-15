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

logger = get_logger("EtherProfile")

def setup(ether, db, owner_id):

# ============================================
# .setpfp Command
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.setpfp$", outgoing=True))
    async def set_pfp_handler(event):
        if event.sender_id != owner_id:
            return

        if not event.is_reply:
            await event.edit("<blockquote>Reply to a photo to set it as your profile picture.</blockquote>")
            return

        reply = await event.get_reply_message()
        if not reply.photo:
            await event.edit("<blockquote>The replied message must be a photo.</blockquote>")
            return

        await event.edit("<blockquote><b>Updating Profile Picture...</b></blockquote>")

        try:
            photo = await reply.download_media()
            await ether(functions.photos.UploadProfilePhotoRequest(
                file=await ether.upload_file(photo)
            ))
            await event.edit("<blockquote><b>Profile Picture Updated Successfully!</b></blockquote>")
            os.remove(photo)
        except Exception as e:
            logger.error(f"PFP update error: {e}")
            await event.edit(f"<blockquote>Error updating PFP: {str(e)}</blockquote>")

# ============================================
# .setbio Command
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.setbio\s+(.+)$", outgoing=True))
    async def set_bio_handler(event):
        if event.sender_id != owner_id:
            return

        bio = event.pattern_match.group(1)
        if len(bio) > 70:
            await event.edit("<blockquote>Bio text is too long (max 70 characters).</blockquote>")
            return

        await event.edit("<blockquote><b>Updating Bio...</b></blockquote>")

        try:
            await ether(functions.account.UpdateProfileRequest(about=bio))
            await event.edit(f"<blockquote><b>Bio updated to:</b>\n<i>{bio}</i></blockquote>")
        except Exception as e:
            logger.error(f"Bio update error: {e}")
            await event.edit(f"<blockquote>Error updating bio: {str(e)}</blockquote>")

# ============================================
# .setname Command
# ============================================

    @ether.on(events.NewMessage(pattern=r"^\.setname\s+(.+)$", outgoing=True))
    async def set_name_handler(event):
        if event.sender_id != owner_id:
            return

        names = event.pattern_match.group(1).split(maxsplit=1)
        first_name = names[0]
        last_name = names[1] if len(names) > 1 else ""

        await event.edit("<blockquote><b>Updating Name...</b></blockquote>")

        try:
            await ether(functions.account.UpdateProfileRequest(
                first_name=first_name,
                last_name=last_name
            ))
            full_name = f"{first_name} {last_name}".strip()
            await event.edit(f"<blockquote><b>Name updated to:</b> <code>{full_name}</code></blockquote>")
        except Exception as e:
            logger.error(f"Name update error: {e}")
            await event.edit(f"<blockquote>Error updating name: {str(e)}</blockquote>")

    logger.info("Profile Management plugin loaded")
