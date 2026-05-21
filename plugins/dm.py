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

import re
import os
import time
import asyncio

from telethon import events, Button
from telethon.extensions import html
from telethon.tl.functions.contacts import BlockRequest
from telethon.errors import FloodWaitError
from telethon.tl.types import (
    DocumentAttributeAnimated,
    KeyboardButtonUrl,
    KeyboardButtonCallback,
)

from html import escape
from services.dm_service import DMService
from utils.parser import parse_links
from utils.logger import get_logger
from config.config import Config
from core.bot import bot, WELCOME_DATA

logger = get_logger("EtherDM")



# ============================================

# Markdown → HTML Converter

# ============================================

def md_to_html(text: str) -> str:
    
    if not text:
        return ""
    
    # Normalize
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    
    # ============================================
    # Preserve blockquotes
    # ============================================
    
    blockquotes = {}
    
    def store_blockquote(match):
    
        key = f"%%BLOCKQUOTE_{len(blockquotes)}%%"
    
        inner = match.group(1).strip()
    
        blockquotes[key] = (
            f"<blockquote>{inner}</blockquote>"
        )
    
        return key
    
    text = re.sub(
        r"<blockquote>(.*?)</blockquote>",
        store_blockquote,
        text,
        flags=re.DOTALL | re.IGNORECASE
    )
    
    # ============================================
    # Preserve inline code
    # ============================================
    
    code_blocks = {}
    
    def store_code(match):
    
        key = f"%%CODE_{len(code_blocks)}%%"
    
        code_blocks[key] = (
            f"<code>{escape(match.group(1))}</code>"
        )
    
        return key
    
    text = re.sub(
        r"`([^`\n]+)`",
        store_code,
        text
    )
    
    
    # ============================================
    # Bold
    # ============================================
    
    text = re.sub(
        r"\*\*(.+?)\*\*",
        r"<b>\1</b>",
        text,
        flags=re.DOTALL
    )
    
    text = re.sub(
        r"__(.+?)__",
        r"<b>\1</b>",
        text,
        flags=re.DOTALL
    )
    
    # ============================================
    # Italic
    # ============================================
    
    text = re.sub(
        r"(?<![\w_])_([^_\n]+?)_(?![\w_])",
        r"<i>\1</i>",
        text
    )
    
    text = re.sub(
        r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)",
        r"<i>\1</i>",
        text,
        flags=re.DOTALL
    )
    
    # ============================================
    # Strikethrough
    # ============================================
    
    text = re.sub(
        r"~~(.+?)~~",
        r"<s>\1</s>",
        text,
        flags=re.DOTALL
    )
    
    # ============================================
    # Restore code blocks
    # ============================================
    
    for key, value in code_blocks.items():
    
        text = text.replace(
            escape(key),
            value
        )
    
        text = text.replace(
            key,
            value
        )
    
    # ============================================
    # Restore blockquotes
    # ============================================
    
    for key, value in blockquotes.items():
    
        text = text.replace(
            escape(key),
            value
        )
    
        text = text.replace(
            key,
            value
        )
    
    # ============================================
    # Cleanup
    # ============================================
    
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )
    
    return text.strip()


# ============================================
# Default Welcome Content
# ============================================

DEFAULT_WELCOME_TEXT = (
    "<blockquote>"
    "👋 <b>Welcome!</b>\n\n"
    "You have reached my private inbox. I am currently unavailable.\n\n"
    "<i>Please leave your message and I will get back to you as soon as possible.</i>\n\n"
    "🛡 <b>Protected by Ether</b>"
    "</blockquote>"
)

DEFAULT_WELCOME_IMAGE = "assets/ether_logo.png"

DEFAULT_WELCOME_BUTTONS = [
    [
        {
            "text": "Userbot Repo",
            "url": "https://github.com/LearningBotsOfficial/Ether",
            "type": "url"
        }
    ]
]

BUTTON_PATTERN = r"\[Button\.(url|inline)\(['\"]([^'\"]+)['\"],\s*['\"]([^'\"]+)['\"]\)\]"


# ============================================
# Setup
# ============================================

def setup(ether, db, owner_id):

    dm_service = DMService(db)
    max_warns = Config.DM_MAX_WARNS

    # ============================================
    # Load Welcome Cache
    # ============================================

    async def load_welcome_data():

        try:

            welcome_config = await dm_service.get_welcome(owner_id)

            if not welcome_config:
                return

            WELCOME_DATA["text"] = (
                welcome_config.get("text")
                or DEFAULT_WELCOME_TEXT
            )

            # Media persistence
            saved_image = welcome_config.get("image")

            if saved_image and os.path.exists(saved_image):
                WELCOME_DATA["image"] = saved_image
            else:
                WELCOME_DATA["image"] = DEFAULT_WELCOME_IMAGE

            WELCOME_DATA["buttons"] = (
                welcome_config.get("buttons")
                or DEFAULT_WELCOME_BUTTONS
            )

            WELCOME_DATA["media_type"] = (
                welcome_config.get("media_type")
                or "photo"
            )

        except Exception as e:
            logger.error(
                f"[WELCOME CACHE ERROR] {e}"
            )

    from utils.task_helper import safe_run

    safe_run(
        load_welcome_data(),
        name="LoadWelcomeData"
    )

    # ============================================
    # Allow Command
    # ============================================

    @ether.on(events.NewMessage(
        pattern=r"^\.allow$",
        outgoing=True
    ))
    async def allow_handler(event):

        if event.sender_id != owner_id:
            return

        if not event.is_private:

            await event.edit(
                "<blockquote>❌ Use in private chat.</blockquote>"
            )

            return

        user_id = event.chat_id

        try:

            user = await dm_service.get_user(user_id)

            if not user:
                await dm_service.create_user(user_id)

            await dm_service.allow_user(user_id)

            logger.info(
                f"[USER ALLOWED] USER={user_id}"
            )

            await event.edit(
                "<blockquote>✅ User allowed.</blockquote>"
            )

        except Exception as e:

            logger.error(
                f"[ALLOW ERROR] USER={user_id} ERROR={e}"
            )

            await event.edit(
                "<blockquote>❌ Failed to allow user.</blockquote>"
            )

    # ============================================
    # Disallow Command
    # ============================================

    @ether.on(events.NewMessage(
        pattern=r"^\.disallow$",
        outgoing=True
    ))
    async def disallow_handler(event):

        if event.sender_id != owner_id:
            return

        if not event.is_private:

            await event.edit(
                "<blockquote>❌ Use in private chat.</blockquote>"
            )

            return

        user_id = event.chat_id

        try:

            await dm_service.disallow_user(
                user_id,
                owner_id
            )

            await event.edit(
                "<blockquote>🚫 User disallowed.</blockquote>"
            )

        except Exception as e:

            logger.error(
                f"[DISALLOW ERROR] USER={user_id} ERROR={e}"
            )

            await event.edit(
                "<blockquote>❌ Failed to disallow user.</blockquote>"
            )

    # ============================================
    # Set Welcome Command
    # ============================================

    @ether.on(events.NewMessage(
        pattern=r"^\.setwelcome(?:\s+([\s\S]*))?$",
        outgoing=True
    ))
    async def setwelcome_handler(event):

        if event.sender_id != owner_id:
            return

        custom_text = (
            event.pattern_match.group(1)
            or ""
        ).strip()

        msg = (
            await event.get_reply_message()
            if event.is_reply else None
        )

        # ============================================
        # Help Menu
        # ============================================

        if not custom_text and msg is None:

            await event.reply(
                "<blockquote>"
                "⚠️ <b>How to use .setwelcome</b>\n\n"

                "📌 <b>Option 1 — Inline text</b>\n"
                "<code>.setwelcome your text here</code>\n\n"

                "📌 <b>Option 2 — Reply mode</b>\n"
                "Reply to any message (text/photo/video)\n"
                "then send:\n"
                "<code>.setwelcome</code>\n\n"

                "🧾 <b>Formatting Supported</b>\n"
                "• <code>&lt;blockquote&gt;text&lt;/blockquote&gt;</code>\n"
                "• <code>**bold**</code>\n"
                "• <code>_italic_</code>\n"
                "• <code>`code`</code>\n"
                "• <code>~~strike~~</code>\n\n"

                "🔘 <b>Buttons Format</b>\n"
                "<code>[Button.url('Google', 'https://google.com')]</code>\n\n"

                "📎 <b>Multiple Buttons (Same Row)</b>\n"
                "<code>"
                "[Button.url('A', 'https://a.com') | "
                "Button.url('B', 'https://b.com')]"
                "</code>\n\n"

                "💡 <b>Note:</b> Default welcome button is used if not set."
                "</blockquote>",
                parse_mode="html"
            )

            return

        # ============================================
        # Media Handling
        # ============================================

        image_path = None
        media_type = "photo"

        os.makedirs("media", exist_ok=True)

        unique_media_name = f"welcome_{owner_id}"

        if msg is not None:

            if msg.photo:

                try:
                    image_path = await msg.download_media(
                        file=f"media/{unique_media_name}.jpg"
                    )
                    media_type = "photo"
                except Exception as e:
                    logger.error(f"[PHOTO DOWNLOAD ERROR] {e}")

            elif msg.video:

                try:
                    image_path = await msg.download_media(
                        file=f"media/{unique_media_name}.mp4"
                    )

                    if (
                        msg.document
                        and any(
                            isinstance(a, DocumentAttributeAnimated)
                            for a in msg.document.attributes
                        )
                    ):
                        media_type = "gif"
                    else:
                        media_type = "video"

                except Exception as e:
                    logger.error(f"[VIDEO DOWNLOAD ERROR] {e}")

            elif (
                msg.document
                and msg.document.mime_type
                and any(
                    msg.document.mime_type.startswith(t)
                    for t in ['image/', 'video/']
                )
            ):

                try:

                    ext = (
                        ".jpg"
                        if msg.document.mime_type.startswith('image/')
                        else ".mp4"
                    )

                    image_path = await msg.download_media(
                        file=f"media/{unique_media_name}{ext}"
                    )

                    media_type = (
                        "photo"
                        if ext == ".jpg"
                        else "video"
                    )

                except Exception as e:
                    logger.error(f"[MEDIA DOWNLOAD ERROR] {e}")

        # ============================================
        # TEXT HANDLING (FIXED CAPTION SUPPORT)
        # ============================================

        raw_text = ""

        if custom_text:
            raw_text = custom_text

        elif msg is not None:
            raw_text = (
                msg.message
                or msg.text
                or msg.caption
                or ""
            )

        raw_text = raw_text.replace("\r\n", "\n")

        try:
            parsed_text = md_to_html(raw_text)
        except Exception as e:
            logger.error(f"[TEXT PARSE ERROR] {e}")
            parsed_text = raw_text

        # ============================================
        # BUTTON PARSING (FIXED SAFE MODE)
        # ============================================

        BUTTON_PATTERN = re.compile(
            r"Button\.(url|inline)\(\s*['\"](.*?)['\"]\s*,\s*['\"](.*?)['\"]\s*\)"
        )

        raw_text_for_buttons = raw_text.strip()

        parsed_text = re.sub(
            r"\[Button\.(?:url|inline)\([^\]]+\)\s*(?:\|\s*Button\.(?:url|inline)\([^\]]+\)\s*)*\]",
            "",
            parsed_text,
            flags=re.MULTILINE
        ).strip()

        buttons = []

        # ============================================
        # Telegram Native Buttons
        # ============================================

        if (
            msg is not None
            and msg.reply_markup
            and hasattr(msg.reply_markup, "rows")
        ):

            button_rows = []

            for row in msg.reply_markup.rows:

                row_buttons = []

                for btn in row.buttons:

                    if isinstance(btn, KeyboardButtonUrl):

                        row_buttons.append({
                            "text": btn.text,
                            "url": btn.url,
                            "type": "url"
                        })

                    elif isinstance(btn, KeyboardButtonCallback):

                        row_buttons.append({
                            "text": btn.text,
                            "data": btn.data.decode(),
                            "type": "callback"
                        })

                if row_buttons:
                    button_rows.append(row_buttons)

            if button_rows:
                buttons = button_rows

        # ============================================
        # INLINE BUTTON PARSING
        # ============================================

        if not buttons:

            button_rows = []

            for line in raw_text_for_buttons.split("\n"):

                line = line.strip()

                matches = BUTTON_PATTERN.findall(line)

                if not matches:
                    continue

                row_buttons = []

                for btn_type, btn_text, btn_value in matches:

                    if btn_type == "url":

                        row_buttons.append({
                            "text": btn_text.strip(),
                            "url": btn_value.strip(),
                            "type": "url"
                        })

                    elif btn_type == "inline":

                        row_buttons.append({
                            "text": btn_text.strip(),
                            "data": btn_value.strip(),
                            "type": "callback"
                        })

                if row_buttons:
                    button_rows.append(row_buttons)

            if button_rows:
                buttons = button_rows

        # ============================================
        # SAVE WELCOME
        # ============================================

        try:

            buttons = buttons or []

            await dm_service.set_welcome(
                owner_id,
                parsed_text,
                image_path,
                buttons,
                media_type
            )

            WELCOME_DATA["text"] = parsed_text
            WELCOME_DATA["image"] = image_path or DEFAULT_WELCOME_IMAGE
            WELCOME_DATA["buttons"] = buttons
            WELCOME_DATA["media_type"] = media_type

            response = (
                "<blockquote>"
                "✅ Welcome message saved."
            )

            if image_path:
                response += f"\n📷 {media_type.capitalize()} included."

            if buttons:
                response += f"\n🔘 {len(buttons)} button row(s) included."

            response += "</blockquote>"

            await event.edit(response, parse_mode="html")

        except Exception as e:

            logger.error(f"[WELCOME SAVE ERROR] {e}")

            await event.edit(
                "<blockquote>❌ Failed to save welcome message.</blockquote>",
                parse_mode="html"
            )

    # ============================================
    # Clear Welcome Command
    # ============================================

    @ether.on(events.NewMessage(
        pattern=r"^\.clearwelcome$",
        outgoing=True
    ))
    async def clearwelcome_handler(event):

        if event.sender_id != owner_id:
            return

        try:

            await dm_service.delete_welcome(owner_id)

            WELCOME_DATA["text"] = None
            WELCOME_DATA["image"] = None
            WELCOME_DATA["buttons"] = None
            WELCOME_DATA["media_type"] = "photo"

            await event.edit(
                "<blockquote>"
                "🗑️ Welcome message cleared."
                "</blockquote>"
            )

        except Exception as e:

            logger.error(
                f"[CLEAR WELCOME ERROR] {e}"
            )

            await event.edit(
                "<blockquote>"
                "❌ Failed to clear welcome."
                "</blockquote>"
            )


    # ============================================
    # DM Handler Helpers
    # ============================================
    
    async def should_ignore_message(event) -> bool:
    
        try:
            if event.sender and getattr(event.sender, 'bot', False):
                return True
    
            sender = await event.get_sender()
    
            if sender:
    
                # Ignore bots
                if getattr(sender, 'bot', False):
                    return True
    
                # Ignore deleted accounts
                if getattr(sender, 'deleted', False):
                    return True
    
        except Exception as e:
            logger.error(f"[IGNORE CHECK ERROR] {e}")
            return True
    
        # Ignore owner
        if event.sender_id == owner_id:
            return True
    
        # Ignore service messages
        if getattr(event, "action", None):
            return True
    
        # Ignore reactions
        if getattr(event, "reactions", None):
            return True
    
        # Ignore stickers
        if event.sticker:
            return True
    
        # Ignore gifs
        if event.gif:
            return True
    
        # Ignore safe commands
        safe_commands = ["/start", "/help", "/ping"]
    
        message_text = (event.raw_text or "").strip().lower()
    
        if message_text in safe_commands:
            return True
    
        # Ignore empty updates
        if not message_text and not event.media:
            return True
    
        return False
    
    
    async def get_or_create_user(user_id):
    
        user = await dm_service.get_user(user_id)
    
        if not user:
            await dm_service.create_user(user_id)
            user = await dm_service.get_user(user_id)
    
        return user
    
    async def send_welcome_message(
        event,
        text,
        welcome_image,
        welcome_buttons,
        welcome_media_type
    ):
    
        try:
    
            bot_username = Config.BOT_USERNAME
    
            # ============================================
            # INLINE MODE
            # ============================================
    
            if bot_username:
    
                WELCOME_DATA["text"] = text
                WELCOME_DATA["buttons"] = welcome_buttons or []
                WELCOME_DATA["image"] = welcome_image
                WELCOME_DATA["media_type"] = welcome_media_type
    
                try:
    
                    results = await ether.inline_query(
                        bot_username,
                        "welcome"
                    )
    
                    if results:
                        await results[0].click(event.chat_id)
                        return
    
                except FloodWaitError as e:
                    logger.warning(f"[INLINE FLOODWAIT] {e.seconds}s")
    
                except Exception as e:
                    logger.error(f"[INLINE ERROR] {e}")
    
            # ============================================
            # BUILD BUTTONS
            # ============================================
    
            keyboard = None
    
            if welcome_buttons:
    
                keyboard = []
    
                for row in welcome_buttons:
    
                    row_buttons = []
    
                    for btn in row:
    
                        if btn["type"] == "url":
                            row_buttons.append(
                                Button.url(btn["text"], btn["url"])
                            )
    
                        elif btn["type"] == "callback":
                            row_buttons.append(
                                Button.inline(btn["text"], btn["data"])
                            )
    
                    if row_buttons:
                        keyboard.append(row_buttons)
    
            # ============================================
            # FALLBACK SEND
            # ============================================
    
            if welcome_image:
    
                await event.respond(
                    file=welcome_image,
                    message=text,
                    buttons=keyboard,
                    parse_mode="html"
                )
    
            else:
    
                await event.respond(
                    text,
                    buttons=keyboard,
                    parse_mode="html"
                )
    
        except Exception as e:
            logger.error(f"[WELCOME SEND ERROR] {e}")
    
    
    async def send_warning(
        event,
        warns,
        max_warns
    ):
    
        try:
    
            warning_msg = (
                f"<blockquote>"
                f"⚠️ <b>Warning {warns}/{max_warns}</b>\n"
                f"Please wait for a reply.\n"
                f"Spamming may result in a block."
                f"</blockquote>"
            )
    
            await event.reply(
                warning_msg,
                parse_mode='html'
            )
    
        except Exception as e:
            logger.error(
                f"[WARNING ERROR] {e}"
            )
    


    # ============================================
    # Spam Detection Handler
    # ============================================

    async def handle_spam_detection(
        event,
        user,
        user_id
    ):

        warns = int(
            user.get("warns", 0)
        )

        warns += 1

        message_text = (
            event.raw_text or ""
        ).strip()

        # Save state
        await dm_service.update_user(
            user_id,
            {
                "warns": warns,
                "message_count": user.get(
                    "message_count",
                    0
                ) + 1,
                "last_message_text": message_text
            }
        )

        return warns

    # ============================================
    # Set DM Warn Limit
    # ============================================

    @ether.on(events.NewMessage(
        pattern=r"^\.setwarn\s+(\d+)$",
        outgoing=True
    ))
    async def setwarnlimit_handler(event):

        if event.sender_id != owner_id:
            return

        try:

            limit = int(
                event.pattern_match.group(1)
            )

            if limit < 1:

                await event.edit(
                    "<blockquote>"
                    "❌ Limit must be greater than 0."
                    "</blockquote>",
                    parse_mode="html"
                )

                return

            Config.DM_MAX_WARNS = limit

            global max_warns
            max_warns = limit

            await event.edit(
                f"<blockquote>"
                f"✅ DM warn limit updated to "
                f"<b>{limit}</b>."
                f"</blockquote>",
                parse_mode="html"
            )

        except Exception as e:

            logger.error(
                f"[SET WARN LIMIT ERROR] {e}"
            )

            await event.edit(
                "<blockquote>"
                "❌ Failed to update warn limit."
                "</blockquote>",
                parse_mode="html"
            )


    
    # ============================================
    # Main DM Handler
    # ============================================
        
    @ether.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
    async def dm_handler(event):
    
        logger.info(
            f"[DM CHECK] USER={event.sender_id}"
        )
    
        # ============================================
        # Ignore unwanted events
        # ============================================
    
        if await should_ignore_message(event):
            return
    
    
        if db is None:
            return
    
        user_id = event.sender_id
    
        user = await get_or_create_user(user_id)
    
        if not user:
            return
    
        # ============================================
        # Welcome config
        # ============================================
    
        welcome_config = await dm_service.get_welcome(owner_id) or {}
    
        welcome_text = (
            welcome_config.get("text")
            or DEFAULT_WELCOME_TEXT
        )
    
        # ============================================
        # Media
        # ============================================
    
        saved_image = welcome_config.get("image")
    
        if saved_image and os.path.exists(saved_image):
            welcome_image = saved_image
        else:
            welcome_image = DEFAULT_WELCOME_IMAGE
    
    
        welcome_buttons = welcome_config.get("buttons", [])
    
        # ============================================
        # Media type
        # ============================================
    
        welcome_media_type = (
            welcome_config.get("media_type")
            or "photo"
        )
    
        # ============================================
        # Blocked users
        # ============================================
    
        if user.get("blocked"):
    
            try:
                await ether(BlockRequest(user_id))
    
            except Exception as e:
                logger.error(
                    f"[BLOCKED USER ERROR] {e}"
                )
    
            return
    
        # ============================================
        # Allowed users
        # ============================================
    
        if user.get("allowed"):
    
            await dm_service.increment_message_count(user_id)
            return
    
        # ============================================
        # Max warns
        # ============================================
    
        max_warns = await dm_service.get_max_warns(
            user_id,
            owner_id
        )
    
        # ============================================
        # First message
        # ============================================
    
        is_first_message = (
            user.get("message_count", 0) == 0
        )
    
        if is_first_message:
    
            await dm_service.update_user(
                user_id,
                {
                    "message_count": 1,
                    "last_message_time": int(time.time()),
                    "warns": user.get("warns", 0)
                }
            )
    
            await send_welcome_message(
                event,
                welcome_text,
                welcome_image,
                welcome_buttons,
                welcome_media_type
            )
    
            return
    
        # ============================================
        # Spam detection
        # ============================================
    
        warns = await handle_spam_detection(
            event,
            user,
            user_id
        )
    
        logger.warning(
            f"[SPAM CHECK] USER={user_id} WARNS={warns}/{max_warns}"
        )
    
        # ============================================
        # Block user
        # ============================================
        
        if warns >= max_warns:
        
            logger.warning(
                f"[USER BLOCKED] USER={user_id}"
            )
        
            try:
        
                await event.respond(
                    "<blockquote>⛔ You have been blocked for spamming.</blockquote>",
                    parse_mode="html"
                )
        
                await asyncio.sleep(1)
        
                await dm_service.block_user(user_id)
                await ether(BlockRequest(user_id))
        
            except Exception as e:
                logger.error(
                    f"[BLOCK ERROR] USER={user_id} ERROR={e}"
                )
        
            return
    
        # ============================================
        # Warning reply
        # ============================================
    
        await send_warning(
            event,
            warns,
            max_warns
        )
        
    
    # ============================================
    # Auto Allow User
    # ============================================
    
    @ether.on(events.NewMessage(outgoing=True))
    async def auto_allow_on_reply(event):
    
        if event.sender_id != owner_id:
            return
    
        if not event.is_private:
            return
    
        if not event.is_reply:
            return
    
        user_id = event.chat_id
    
        try:
    
            user = await get_or_create_user(user_id)
    
            if not user:
                return
    
            # Already allowed
            if user.get("allowed"):
                return
    
            # Auto allow
            await dm_service.allow_user(user_id)
    
        except Exception as e:
            logger.error(
                f"[AUTO ALLOW ERROR] USER={user_id} ERROR={e}"
            )