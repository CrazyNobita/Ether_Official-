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

from telethon import TelegramClient
from telethon.sessions import StringSession
from config.config import Config
from utils.logger import get_logger

logger = get_logger("EtherUserClient")


class EtherUserClient:
    
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

# ============================================
# Client Management
# ============================================

    def init_client(self, session_string: str = None):
        """
        (Re)initialize the TelegramClient.
        - If a session_string is provided, resume the existing session from MongoDB.
        - Otherwise, create a fresh blank StringSession (will require login).
        """
        session = StringSession(session_string) if session_string else StringSession()
        self._client = TelegramClient(
            session,
            Config.API_ID,
            Config.API_HASH
        )
        self._client.parse_mode = 'html'
        logger.info("Session: Client initialized with %s session." % ("stored" if session_string else "blank"))
        return self._client

    @property
    def client(self) -> TelegramClient:
        if self._client is None:
            self.init_client()
        return self._client

    def get_session_string(self) -> str:
        """Export the current session as a string for storage in MongoDB."""
        if self._client and self._client.session:
            return self._client.session.save()
        return None

    async def connect(self) -> bool:
        try:
            await self.client.connect()
            logger.info("Telegram client connected")
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

    async def disconnect(self) -> None:
        try:
            if self._client and self._client.is_connected():
                await self._client.disconnect()
                logger.info("Telegram client disconnected")
        except Exception as e:
            logger.error(f"Disconnect error: {e}")

    async def is_authorized(self) -> bool:
        try:
            return await self.client.is_user_authorized()
        except Exception as e:
            logger.error(f"Auth check failed: {e}")
            return False

    def get_client(self) -> TelegramClient:
        return self.client