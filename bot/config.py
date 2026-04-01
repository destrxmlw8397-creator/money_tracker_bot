"""
Configuration Module
Loads environment variables and provides configuration settings
"""

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Config:
    """Application Configuration"""
    
    # Telegram Configuration
    API_ID = int(os.getenv('API_ID'))
    API_HASH = os.getenv('API_HASH')
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Server Configuration
    PORT = int(os.environ.get('PORT', 10000))
    
    # Application Configuration
    TIMEZONE = 'Asia/Dhaka'
    ITEMS_PER_PAGE = 10
    TEMP_DATA_EXPIRY_HOURS = 12
    
    # Default Wallets
    DEFAULT_WALLETS = {"Cash": 0.0, "Bank": 0.0, "Bkash": 0.0}
    
    @classmethod
    def validate(cls):
        """
        Validate required configuration settings
        
        Raises:
            ValueError: If any required config is missing
        """
        required = ['API_ID', 'API_HASH', 'BOT_TOKEN', 'DATABASE_URL']
        missing = []
        
        for req in required:
            if not getattr(cls, req):
                missing.append(req)
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        return True
