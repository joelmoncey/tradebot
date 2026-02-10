import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
    TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
    TELEGRAM_SESSION_NAME = os.getenv("TELEGRAM_SESSION_NAME", "groww_bot_session")
    
    GROWW_API_KEY = os.getenv("GROWW_API_KEY")
    GROWW_API_SECRET = os.getenv("GROWW_API_SECRET")
    GROWW_AUTH_TOKEN = os.getenv("GROWW_AUTH_TOKEN")
    
    TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
    
    DRY_RUN = os.getenv("DRY_RUN", "True").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls):
        missing = []
        if not cls.TELEGRAM_API_ID: missing.append("TELEGRAM_API_ID")
        if not cls.TELEGRAM_API_HASH: missing.append("TELEGRAM_API_HASH")
        if not cls.TELEGRAM_CHANNEL_ID: missing.append("TELEGRAM_CHANNEL_ID")
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
