import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application Configuration"""
    
    # Telegram Config
    API_ID = int(os.getenv('API_ID'))
    API_HASH = os.getenv('API_HASH')
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    # Database Config
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Server Config
    PORT = int(os.environ.get("PORT", 10000))
    
    # App Config
    TIMEZONE = 'Asia/Dhaka'
    ITEMS_PER_PAGE = 10
    TEMP_DATA_EXPIRY_HOURS = 12
    
    # Default Wallets
    DEFAULT_WALLETS = {"Cash": 0.0, "Bank": 0.0, "Bkash": 0.0}
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required = ['API_ID', 'API_HASH', 'BOT_TOKEN', 'DATABASE_URL']
        missing = [r for r in required if not getattr(cls, r)]
        if missing:
            raise ValueError(f"Missing required config: {missing}")
        return True
