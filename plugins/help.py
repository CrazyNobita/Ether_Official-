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
from config.config import Config
from utils.logger import get_logger
from core.bot import bot

logger = get_logger("EtherHelp")


def setup(ether, db, owner_id):
    
    @ether.on(events.NewMessage(pattern=r"^\.help$", outgoing=True))
    async def help_handler(event):
        user = event.sender_id
        if user != Config.OWNER_ID:
            return
        
        bot_username = Config.BOT_USERNAME
        if not bot_username:
            await event.reply(
                "<blockquote>"
                "🔥 <b>Ether Help</b>\n\n"
                "<code>.commands</code> - List all commands\n"
                "<code>.ping</code> - Check latency\n"
                "<code>.shortcut &lt;name&gt;</code> - Save shortcut\n"
                "<code>.get &lt;name&gt;</code> - Get shortcut\n"
                "<code>.setwelcome</code> - Set welcome\n"
                "<code>.allow</code> - Allow user\n"
                "<code>.disallow</code> - Disallow user\n\n"
                "<i>Bot identity not initialized. Please wait or check your BOT_TOKEN.</i>"
                "</blockquote>",
                
            )
            return
        
        try:
            await event.delete()
            
            results = await ether.inline_query(bot_username, "help")
            
            if results:
                await results[0].click(event.chat_id)
            else:
                await event.respond(
                    "<blockquote>"
                    "🔥 <b>Ether Help</b>\n\n"
                    "<code>.commands</code> - List all commands\n"
                    "<code>.ping</code> - Check latency\n"
                    "<code>.shortcut &lt;name&gt;</code> - Save shortcut\n"
                    "<code>.get &lt;name&gt;</code> - Get shortcut\n"
                    "<code>.setwelcome</code> - Set welcome\n"
                    "<code>.allow</code> - Allow user\n\n"
                    "<i>Bot inline query failed.</i>"
                    "</blockquote>",
                    
                )
        except Exception as e:
            logger.error(f"Inline help failed: {e}")
            await event.respond(
                "<blockquote>"
                "🔥 <b>Ether Help</b>\n\n"
                "<code>.commands</code> - List all commands\n"
                "<code>.ping</code> - Check latency\n"
                "<code>.shortcut &lt;name&gt;</code> - Save shortcut\n"
                "<code>.get &lt;name&gt;</code> - Get shortcut\n"
                "<code>.setwelcome</code> - Set welcome\n"
                "<code>.allow</code> - Allow user\n"
                "<code>.disallow</code> - Disallow user"
                "</blockquote>",
                
            )
    
    @ether.on(events.NewMessage(pattern=r"^\.commands$", outgoing=True))
    async def commands_handler(event):
        if event.sender_id != owner_id:
            return
            
        command_list = (
            "<blockquote>"
            "📜 <b>Available Commands</b>\n\n"
            "<b>System:</b>\n"
            "• <code>.alive</code> - System status\n"
            "• <code>.ping</code> - Check latency\n"
            "• <code>.help</code> - Interactive help\n"
            "• <code>.commands</code> - This list\n"
            "• <code>.restart</code> - Reboot bot\n\n"
            "<b>DMs & Protection:</b>\n"
            "• <code>.allow</code> - Allow user\n"
            "• <code>.disallow</code> - Disallow user\n"
            "• <code>.setwelcome</code> - Set DM welcome\n"
            "• <code>.clearwelcome</code> - Clear DM welcome\n"
            "• <code>.setwarn &lt;n&gt;</code> - Set max warns\n"
            "• <code>.shield</code> - Shield control\n"
            "• <code>.autoread &lt;on/off&gt;</code> - Toggle auto-read\n\n"
            "<b>Shortcuts:</b>\n"
            "• <code>.shortcut &lt;name&gt;</code> - Save reply\n"
            "• <code>.get &lt;name&gt;</code> - Send shortcut\n"
            "• <code>.shortcuts</code> - List all\n"
            "• <code>.delshortcut &lt;name&gt;</code> - Delete\n\n"
            "<b>Utility:</b>\n"
            "• <code>.tagall &lt;msg&gt;</code> - Mention all\n"
            "• <code>.fonts &lt;text&gt;</code> - Style text\n"
            "</blockquote>"
        )
        
        await event.edit(command_list)

    logger.info("Help plugin loaded (inline mode)")
