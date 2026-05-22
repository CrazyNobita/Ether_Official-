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
# =============================================================================

import asyncio
import signal
import sys
import os

from contextlib import suppress

from core.user_client import EtherUserClient
from core.bot import ether_bot, set_userbot_client, set_plugin_loader
from core.loader import PluginLoader
from storage.mongo import ether_db
from config.config import Config
from config.channels import validate_integrity
from utils.logger import setup_logger, get_logger

# -----------------------------------------------------------------------------
# LOGGER
# -----------------------------------------------------------------------------

setup_logger()
logger = get_logger("EtherMain")

# -----------------------------------------------------------------------------
# GLOBALS
# -----------------------------------------------------------------------------

shutdown_event = asyncio.Event()
plugin_loader = None

# -----------------------------------------------------------------------------
# KEEP ALIVE
# -----------------------------------------------------------------------------

async def keep_alive():
    while not shutdown_event.is_set():
        logger.info("⚡ Ether Alive")
        await asyncio.sleep(300)

# -----------------------------------------------------------------------------
# USERBOT
# -----------------------------------------------------------------------------

async def run_userbot():
    global plugin_loader

    try:
        logger.info("🚀 Starting Userbot")

        # MongoDB
        if await ether_db.connect():
            logger.info("✅ MongoDB Connected")
        else:
            logger.warning("⚠️ MongoDB Connection Failed")

        # Session Check
        session_file = f"{Config.SESSION_NAME}.session"

        if os.path.exists(session_file):
            logger.info(f"✅ Session Found: {session_file}")
        else:
            logger.warning(f"⚠️ Session Missing: {session_file}")

        # User Client
        client_wrapper = EtherUserClient()

        if not await client_wrapper.connect():
            logger.error("❌ Failed To Connect User Client")
            return

        logger.info("✅ User Client Connected")

        # Authorization Check
        if await client_wrapper.is_authorized():
            logger.info("✅ Userbot Authorized")
        else:
            logger.warning("⚠️ Userbot Not Authorized")
            logger.warning("Use /login")

        client = client_wrapper.get_client()

        # Set Global References
        set_userbot_client(client, client_wrapper)

        # Plugin Loader
        plugin_loader = PluginLoader(
            client=client,
            db=ether_db.db,
            owner_id=Config.OWNER_ID
        )

        plugin_loader.load_all()

        set_plugin_loader(plugin_loader)

        stats = plugin_loader.get_stats()

        logger.info(f"✅ Plugins Loaded: {stats['total']}")
        logger.info(f"📦 {stats['plugins']}")
        logger.info("🤖 Userbot Running")

        # Run Forever
        await client.run_until_disconnected()

    except asyncio.CancelledError:
        logger.warning("⚠️ Userbot Cancelled")

    except Exception as e:
        logger.error(f"❌ Userbot Error: {e}", exc_info=True)

# -----------------------------------------------------------------------------
# BOT
# -----------------------------------------------------------------------------

async def run_bot():
    try:
        if not Config.BOT_TOKEN:
            logger.warning("⚠️ BOT_TOKEN Missing")
            return

        logger.info("🚀 Starting Bot")

        await ether_bot.start()

        me = await ether_bot.get_me()

        logger.info(f"✅ Bot Started: @{me.username}")
        logger.info("🤖 Bot Running")

        await asyncio.Event().wait()

    except asyncio.CancelledError:
        logger.warning("⚠️ Bot Cancelled")

    except Exception as e:
        logger.error(f"❌ Bot Error: {e}", exc_info=True)

# -----------------------------------------------------------------------------
# STARTUP
# -----------------------------------------------------------------------------

async def startup():
    logger.info("════════════════════════════")
    logger.info("🚀 Ether Starting")
    logger.info("════════════════════════════")

    # Security Check
    if not validate_integrity():
        logger.error("❌ SECURITY VIOLATION")
        sys.exit(1)

    logger.info("✅ Integrity Validated")

    tasks = [
        asyncio.create_task(run_bot(), name="BotTask"),
        asyncio.create_task(run_userbot(), name="UserbotTask"),
        asyncio.create_task(keep_alive(), name="KeepAliveTask")
    ]

    logger.info("✅ All Systems Started")

    await shutdown_event.wait()

    logger.warning("⚠️ Shutdown Signal Received")

    for task in tasks:
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)

# -----------------------------------------------------------------------------
# SHUTDOWN
# -----------------------------------------------------------------------------

async def shutdown():
    logger.info("🛑 Shutting Down")

    with suppress(Exception):
        await ether_bot.stop()

    with suppress(Exception):
        await ether_db.close()

    logger.info("✅ Shutdown Complete")

# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------

async def main():
    loop = asyncio.get_running_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        with suppress(NotImplementedError):
            loop.add_signal_handler(sig, shutdown_event.set)

    try:
        await startup()

    except KeyboardInterrupt:
        logger.warning("⚠️ Interrupted")

    except Exception as e:
        logger.error(f"❌ Fatal Error: {e}", exc_info=True)

    finally:
        await shutdown()

# -----------------------------------------------------------------------------
# ENTRY
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        asyncio.run(main())

    except Exception as e:
        logger.error(f"❌ Runtime Error: {e}", exc_info=True)
