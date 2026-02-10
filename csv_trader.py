import asyncio
import logging
import pandas as pd
import time
from config import Config
from groww_trader import GrowwTrader

logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

CSV_FILE = "trade_signals.csv"
POLL_INTERVAL = 5  # Seconds

class CSVTrader:
    def __init__(self):
        self.trader = GrowwTrader()
        self.processed_ids = set()
        self.load_processed_ids()

    def load_processed_ids(self):
        try:
            df = pd.read_csv(CSV_FILE)
            # Mark all existing signals as processed on startup to avoid re-trading old info
            if "signal_id" in df.columns:
                self.processed_ids = set(df["signal_id"].tolist())
            logger.info(f"Loaded {len(self.processed_ids)} processed signals.")
        except FileNotFoundError:
            logger.warning("No CSV file found yet. Waiting for creator...")

    def check_for_signals(self):
        try:
            df = pd.read_csv(CSV_FILE)
            new_signals = df[~df["signal_id"].isin(self.processed_ids)]
            
            for _, row in new_signals.iterrows():
                signal_id = row["signal_id"]
                signal = {
                    "symbol": row["symbol"],
                    "action": row["action"],
                    "price": row["price"],
                    "sl": row["stop_loss"],
                    "target": row["target"]
                }
                
                logger.info(f"New signal found: {signal['symbol']} {signal['action']}")
                
                # Execute Trade
                if self.trader.place_order(signal):
                    self.processed_ids.add(signal_id)
                    logger.info(f"Processed signal ID: {signal_id}")
                else:
                    logger.error(f"Failed to process signal ID: {signal_id}")

        except FileNotFoundError:
            pass
        except Exception as e:
            logger.error(f"Error reading CSV: {e}")

    async def start(self):
        logger.info("Starting CSV Trader (CSV -> Groww)...")
        while True:
            self.check_for_signals()
            await asyncio.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    asyncio.run(CSVTrader().start())
