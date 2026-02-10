import re
import logging

class SignalParser:
    def __init__(self):
        # Example patterns:
        # BUY RELIANCE AT 2500 SL 2400 TGT 2600
        # SELL TATASTEEL CMP SL 105 TGT 100
        self.buy_pattern = re.compile(r"(?i)\bBUY\b\s+([A-Z0-9]+)\s+(?:AT\s+)?([\d\.]+)\s+(?:SL\s+)?([\d\.]+)\s+(?:TGT|TARGET)\s+([\d\.]+)")
        self.sell_pattern = re.compile(r"(?i)\bSELL\b\s+([A-Z0-9]+)\s+(?:AT\s+)?([\d\.]+)\s+(?:SL\s+)?([\d\.]+)\s+(?:TGT|TARGET)\s+([\d\.]+)")

    def parse(self, text):
        """
        Parses the text and returns a signal dictionary if a match is found.
        Returns None if no signal is found.
        """
        match_buy = self.buy_pattern.search(text)
        if match_buy:
             return {
                "action": "BUY",
                "symbol": match_buy.group(1),
                "price": float(match_buy.group(2)),
                "sl": float(match_buy.group(3)),
                "target": float(match_buy.group(4))
            }

        match_sell = self.sell_pattern.search(text)
        if match_sell:
             return {
                "action": "SELL",
                "symbol": match_sell.group(1),
                "price": float(match_sell.group(2)),
                "sl": float(match_sell.group(3)),
                "target": float(match_sell.group(4))
            }
        
        return None
