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

    async def monitor_and_execute(self, signal):
        """
        Monitors price if needed, then executes trade for all accounts.
        """
        symbol = signal['symbol']
        trigger_price = signal.get('price')
        
        # Determine if we need to watch locally
        if trigger_price:
            logger.info(f"Starting Local Watcher for {symbol} > {trigger_price}...")
            # Use the first trader to check prices (assuming all see same market data)
            reference_trader = self.traders[0]["trader"]
            
            while True:
                ltp = reference_trader.get_latest_price(symbol)
                if ltp is None:
                    logger.warning(f"Could not fetch LTP for {symbol}. Retrying...")
                    await asyncio.sleep(2)
                    continue
                
                logger.info(f"Watching {symbol}: LTP {ltp} | Trigger {trigger_price}")
                
                # Check for trigger condition
                # Use a small buffer (e.g., 0.5%) or strict check
                if ltp >= trigger_price:
                    logger.info(f"Trigger HIT! {ltp} >= {trigger_price}. Executing orders...")
                    break
                
                await asyncio.sleep(2) # Poll every 2 seconds

        # Create tasks for all accounts
        tasks = []
        for account in self.traders:
            name = account["name"]
            trader = account["trader"]
            logger.info(f"Executing trade for {name}...")
            try:
                # Pass directly since we already waited for the trigger
                # We can now place a MARKET or IMMEDIATE LIMIT order since check passed
                # BUT user might still want SL logic in system.
                # Given user context: "Above is the buying price... set order on groww at buying price"
                # If we bypassed locally, we can now place the order.
                # Let's keep place_order logic which sends SL_LIMIT as a safeguard
                # OR switch to MARKET if price is already crossed.
                # For safety, we just call place_order which sends SL_LIMIT. 
                # Since price >= trigger, SL_LIMIT will execute immediately or sit as pending if price dips back.
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
                
                logger.info(f"New Signal! Starting async monitor task...")
                # Fire and forget the monitor task so we can keep listening for new signals
                asyncio.create_task(self.monitor_and_execute(signal))
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
