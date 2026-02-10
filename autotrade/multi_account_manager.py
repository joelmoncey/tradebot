import asyncio
import logging
import pandas as pd
import json
import os
from config import Config
from groww_trader import GrowwTrader

logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

CSV_FILE = "trade_signals.csv"
ACCOUNTS_FILE = "accounts.json"
POLL_INTERVAL = 5

class MultiAccountManager:
    def __init__(self):
        self.traders = []
        self.processed_ids = set()
        self.load_accounts()
        self.load_processed_ids()

    def load_accounts(self):
        if not os.path.exists(ACCOUNTS_FILE):
             logger.error(f"{ACCOUNTS_FILE} not found!")
             return

        with open(ACCOUNTS_FILE, 'r') as f:
            accounts = json.load(f)
            
        for acc in accounts:
            try:
                trader = GrowwTrader(
                    api_key=acc.get("api_key"),
                    api_secret=acc.get("api_secret"),
                    auth_token=acc.get("auth_token")
                )
                self.traders.append({"name": acc["name"], "trader": trader})
                logger.info(f"Loaded account: {acc['name']}")
            except Exception as e:
                logger.error(f"Failed to load account {acc.get('name')}: {e}")

    def load_processed_ids(self):
        try:
            df = pd.read_csv(CSV_FILE)
            if "signal_id" in df.columns:
                self.processed_ids = set(df["signal_id"].tolist())
        except FileNotFoundError:
            pass

    async def execute_trade_for_all(self, signal):
        tasks = []
        for account in self.traders:
            name = account["name"]
            trader = account["trader"]
            logger.info(f"Executing trade for {name}...")
            # We wrap the synchronous call in a thread run if needed, but for now we'll call directly
            # For true parallelism with blocking IO, we'd use run_in_executor
            # But here we will just call it.
            try:
                success = trader.place_order(signal)
                status = "SUCCESS" if success else "FAILED"
                logger.info(f"Account {name}: {status}")
            except Exception as e:
                logger.error(f"Account {name} failed: {e}")
        
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
                
                logger.info(f"New Signal! Broadcasting to {len(self.traders)} accounts.")
                asyncio.create_task(self.execute_trade_for_all(signal))
                self.processed_ids.add(signal_id)

        except FileNotFoundError:
            pass
        except Exception as e:
            logger.error(f"Error reading CSV: {e}")

    async def start(self):
        logger.info(f"Starting Multi-Account Manager with {len(self.traders)} accounts...")
        while True:
            self.check_for_signals()
            await asyncio.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    asyncio.run(MultiAccountManager().start())
