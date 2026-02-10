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

    def get_lot_size(self, symbol):
        """
        Determines lot size based on symbol name.
        """
        sym = symbol.upper()
        if "BANKNIFTY" in sym:
            return 15
        elif "FINNIFTY" in sym:
            return 25 
        elif "MIDCPNIFTY" in sym:
            return 50 # Verify current lot sizes
        elif "NIFTY" in sym:
            return 25
        elif "SENSEX" in sym:
            return 10
        return 1 # Default for Equity

    def place_order(self, signal):
        """
        Places an order based on the signal.
        For "Above" price (Buy Stop), we use SL-Limit or SL-Market order.
        """
        symbol = signal['symbol']
        buy_price = signal.get('price')
        
        # Calculate Quantity
        quantity = self.get_lot_size(symbol)

        if self.dry_run:
            logger.info(f"[DRY RUN] Would search for '{symbol}' and place Buy Order > {buy_price} (Qty: {quantity})")
            return True

        try:
            # 1. Search for the Scrip ID
            search_results = self.groww.search_scrip(symbol)
            if not search_results or len(search_results) == 0:
                logger.error(f"Could not find scrip for symbol: {symbol}")
                return False
            
            # Assuming the first result is the correct one (usually correct for explicit names)
            scrip = search_results[0]
            search_id = scrip['searchId']
            logger.info(f"Resolved {symbol} to ID: {search_id} ({scrip['displayName']})")

            # 2. Prepare Order Params
            # IF "price" is present, it means "Buy Above X", so use SL Order
            if buy_price and buy_price > 0:
                # Buying ABOVE market price requires a STOP LOSS LIMIT order
                # Trigger Price = buy_price
                # Limit Price = slightly higher to ensure fill (e.g., +0.5% or +1 rupee)
                limit_price = buy_price + 1.0 
                
                order_details = {
                    'exchange': 'NSE',  # Options are usually on NSE
                    'security_id': search_id,
                    'transaction_type': 'BUY',
                    'quantity': quantity, 
                    'price': limit_price,
                    'trigger_price': buy_price,
                    'order_type': 'SL_LIMIT', 
                    'product_type': 'I_FO', # Intraday F&O usually, or 'D_FO' for delivery
                    'validity': 'DAY'
                }
            else:
                # Market Order
                order_details = {
                    'exchange': 'NSE',
                    'security_id': search_id,
                    'transaction_type': 'BUY',
                    'quantity': quantity,
                    'price': 0,
                    'order_type': 'MARKET',
                    'product_type': 'I_FO',
                    'validity': 'DAY'
                }

            logger.info(f"Placing order: {order_details}")
            
            # 3. Execute Order
            # Note: actual method name involves making a dict and sending it
            # Using the simplified wrapper if available, or raw call
            response = self.groww.place_order(**order_details)
            
            logger.info(f"Order Response: {response}")
            return True

        except Exception as e:
            logger.error(f"Failed to place order for {symbol}: {e}")
            return False
