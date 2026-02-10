import asyncio
import logging
import pandas as pd
import uuid
from datetime import datetime
from config import Config
from telegram_bot import TelegramListener
from signal_parser import SignalParser

logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

CSV_FILE = "trade_signals.csv"

def save_signal_to_csv(signal):
    try:
        # Load existing or create new
        try:
            df = pd.read_csv(CSV_FILE)
        except FileNotFoundError:
            df = pd.DataFrame(columns=["timestamp", "signal_id", "symbol", "action", "price", "stop_loss", "target", "status"])

        # Create new row
        new_row = {
            "timestamp": datetime.now().isoformat(),
            "signal_id": str(uuid.uuid4()),
            "symbol": signal['symbol'],
            "action": signal['action'],
            "price": signal['price'],
            "stop_loss": signal['sl'],
            "target": signal['target'],
            "status": "NEW"
        }

        # Append and save
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)
        logger.info(f"Signal saved to CSV: {signal['symbol']} {signal['action']}")
        return True

    except Exception as e:
        logger.error(f"Failed to save to CSV: {e}")
        return False

async def main():
    Config.validate()
    parser = SignalParser()
    
    async def process_message(text):
        signal = parser.parse(text)
        if signal:
            logger.info(f"Signal detected: {signal}")
            save_signal_to_csv(signal)
        else:
            logger.debug(f"No signal found in: {text}")

    logger.info("Starting Signal Loader (Telegram -> CSV)...")
    listener = TelegramListener(process_message)
    await listener.start()

if __name__ == "__main__":
    asyncio.run(main())
