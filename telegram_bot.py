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
        
        # Force cache dialogs to ensure we can find the entity
        # This fixes 'Cannot find entity' errors for clean sessions
        await self.client.get_dialogs() 

        try:
            # Verify we can see the channel
            # Remove any prefix from config for clean conversion if needed, but usually telethon handles it
            channel_id = int(Config.TELEGRAM_CHANNEL_ID)
            entity = await self.client.get_entity(channel_id)
            logger.info(f"Successfully resolved channel: {entity.title} ({entity.id})")
        except ValueError:
            logger.error(f"Could not find channel with ID {Config.TELEGRAM_CHANNEL_ID}. Make sure you are a member of this channel/group!")
            return

        @self.client.on(events.NewMessage(chats=channel_id))
        async def handler(event):
            logger.info(f"New message received: {event.raw_text}")
            await self.callback(event.raw_text)

        logger.info(f"Listening to channel ID: {Config.TELEGRAM_CHANNEL_ID}")
        await self.client.run_until_disconnected()
