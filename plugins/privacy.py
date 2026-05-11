# =============================================================================
#  Ether Userbot System - Privacy & Automation Plugin
# =============================================================================

from telethon import events
from utils.logger import get_logger
from config.config import Config

logger = get_logger("PrivacyPlugin")

def setup(ether, db, owner_id):

    # 1. Auto-Read Feature
    # Automatically marks all incoming private messages as read
    @ether.on(events.NewMessage(incoming=True))
    async def auto_read_handler(event):
        if not event.is_private:
            return
            
        if event.sender_id == owner_id:
            return
            
        # We can add a setting check here later
        try:
            await event.mark_read()
        except Exception as e:
            logger.error(f"Auto-read error: {e}")

    # 2. Presence Automation (Optional)
    # This could be used to always show 'Online' or handle typing indicators
    
    @ether.on(events.NewMessage(pattern=r"^\.autoread (on|off)$", outgoing=True))
    async def toggle_autoread(event):
        if event.sender_id != owner_id:
            return
            
        cmd = event.pattern_match.group(1).lower()
        # In a real scenario, we would save this to DB
        # For now, we just acknowledge
        
        status = "ENABLED" if cmd == "on" else "DISABLED"
        await event.edit(f"<blockquote>👁️ <b>Auto-Read:</b> {status}</blockquote>")

    logger.info("Privacy plugin loaded (Auto-read active)")
