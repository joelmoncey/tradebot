from growwapi import GrowwAPI
import logging
from config import Config

logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class GrowwTrader:
    def __init__(self, api_key=None, api_secret=None, auth_token=None):
        self.dry_run = Config.DRY_RUN
        
        # Use provided credentials or fallback to Config (for backward compatibility/single account)
        self.api_key = api_key or Config.GROWW_API_KEY
        self.api_secret = api_secret or Config.GROWW_API_SECRET
        self.auth_token = auth_token or Config.GROWW_AUTH_TOKEN

        if not self.dry_run:
            try:
                self.groww = GrowwAPI(self.api_key, self.api_secret)
                self.groww.set_access_token(self.auth_token)
                logger.info(f"Groww API authenticated for account.")
            except Exception as e:
                logger.error(f"Failed to authenticate Groww API: {e}")

    def place_order(self, signal):
        """
        Places an order based on the signal.
        """
        if self.dry_run:
            logger.info(f"[DRY RUN] Placing order: {signal}")
            return True

        try:
            # map signal to groww order params
            # This is a simplified example. You need to adapt to actual Groww API methods
            order_type = 'LIMIT' if signal.get('price') else 'MARKET'
            
            # Example call (verify with actual SDK docs)
            # response = self.groww.place_order(...) 
            
            logger.info(f"Order placed for {signal['symbol']}")
            return True
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            return False
