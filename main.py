import asyncio
import logging
from config import Config
from telegram_bot import TelegramListener
from signal_parser import SignalParser
from groww_trader import GrowwTrader

logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

async def main():
    try:
        Config.validate()
        
        parser = SignalParser()
        trader = GrowwTrader()
        
        async def process_message(text):
            signal = parser.parse(text)
            if signal:
                logger.info(f"Signal detected: {signal}")
                trader.place_order(signal)
            else:
                logger.debug(f"No signal found in: {text}")

        listener = TelegramListener(process_message)
        await listener.start()
        
    except Exception as e:
        logger.error(f"Bot crashed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
