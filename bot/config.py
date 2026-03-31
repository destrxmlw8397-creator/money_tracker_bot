import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application Configuration"""
    
    API_ID = int(os.getenv('API_ID'))
    API_HASH = os.getenv('API_HASH')
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    DATABASE_URL = os.getenv('DATABASE_URL')
    PORT = int(os.environ.get('PORT', 10000))
    
    TIMEZONE = 'Asia/Dhaka'
    ITEMS_PER_PAGE = 10
    TEMP_DATA_EXPIRY_HOURS = 12
    
    DEFAULT_WALLETS = {"Cash": 0.0, "Bank": 0.0, "Bkash": 0.0}
    
    @classmethod
    def validate(cls):
        required = ['API_ID', 'API_HASH', 'BOT_TOKEN', 'DATABASE_URL']
        missing = [r for r in required if not getattr(cls, r)]
        if missing:
            raise ValueError(f"Missing required config: {missing}")
        return True
