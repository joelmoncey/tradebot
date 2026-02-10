import re
import logging

class SignalParser:
    def __init__(self):
        # Format 1: BUY RELIANCE AT 2500...
        self.simple_pattern = re.compile(r"(?i)\b(BUY|SELL)\b\s+([A-Z0-9]+)\s+(?:AT\s+)?([\d\.]+)\s+(?:SL\s+)?([\d\.]+)\s+(?:TGT|TARGET)\s+([\d\.]+)")
        
        # Format 2: 
        # NIFTY 26100 PE
        # Above : 185
        # SL : 175
        # TGT : 195...
        self.option_pattern = re.compile(
            r"(?i)^([A-Z\s\d]+(?:CE|PE))\s*\n"   # Line 1: NIFTY 26100 PE (Symbol)
            r".*?Above\s*:\s*([\d\.]+)\s*\n"      # Line 2: Above : 185 (Price)
            r".*?SL\s*:\s*([\d\.]+)\s*\n"         # Line 3: SL : 175 (Stop Loss)
            r".*?TGT\s*:\s*([\d\.]+)",            # Line 4: TGT : 195 (First Target)
            re.MULTILINE | re.DOTALL
        )

    def parse(self, text):
        """
        Parses the text and returns a signal dictionary if a match is found.
        """
        # Try Option Pattern
        match_opt = self.option_pattern.search(text)
        if match_opt:
            return {
                "action": "BUY",  # "Above" implies a Buy Stop/Limit
                "symbol": match_opt.group(1).strip(),
                "price": float(match_opt.group(2)),
                "sl": float(match_opt.group(3)),
                "target": float(match_opt.group(4)),
                "type": "OPTION"
            }

        # Try Simple Pattern
        match_simple = self.simple_pattern.search(text)
        if match_simple:
             return {
                "action": match_simple.group(1).upper(),
                "symbol": match_simple.group(2),
                "price": float(match_simple.group(3)),
                "sl": float(match_simple.group(4)),
                "target": float(match_simple.group(5)),
                "type": "EQUITY"
            }
        
        return None
