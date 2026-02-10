from telethon import TelegramClient, events
import logging
from config import Config

logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class TelegramListener:
    def __init__(self, callback):
        self.client = TelegramClient(Config.TELEGRAM_SESSION_NAME, Config.TELEGRAM_API_ID, Config.TELEGRAM_API_HASH)
        self.callback = callback

    async def start(self):
        logger.info("Connecting to Telegram...")
        await self.client.start()
        logger.info("Connected to Telegram.")

        @self.client.on(events.NewMessage(chats=Config.TELEGRAM_CHANNEL_ID))
        async def handler(event):
            logger.info(f"New message received: {event.raw_text}")
            await self.callback(event.raw_text)

        logger.info(f"Listening to channel ID: {Config.TELEGRAM_CHANNEL_ID}")
        await self.client.run_until_disconnected()
