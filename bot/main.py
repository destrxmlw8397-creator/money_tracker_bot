# bot/main.py - Fixed version

import os
import logging
import threading
import asyncio
from datetime import datetime
from flask import Flask, jsonify
from telethon import TelegramClient, events
from bot.config import Config
from bot.database.connection import init_db, get_db_connection
from bot.utils.logger import setup_logger
from bot.handlers.start import StartHandler
from bot.handlers.balance import BalanceHandler
from bot.handlers.callback import CallbackHandler
from bot.handlers.message import MessageHandler

# Setup
setup_logger()
logger = logging.getLogger(__name__)

# Flask app for health checks
app = Flask(__name__)

@app.route('/')
def health_check():
    """Health check endpoint for Render"""
    try:
        # Test database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
        logger.error(f"Health check DB error: {e}")
    
    return jsonify({
        "status": "online",
        "service": "Money Tracker Bot",
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "version": "1.0.0"
    })

@app.route('/health')
def health():
    """Simple health check"""
    return "OK", 200

class MoneyTrackerBot:
    """Main Bot Class"""
    
    def __init__(self):
        self.client = TelegramClient('bot_session', Config.API_ID, Config.API_HASH)
        
        # Initialize handlers
        self.start_handler = StartHandler(self.client)
        self.balance_handler = BalanceHandler(self.client)
        self.callback_handler = CallbackHandler(self.client)
        self.message_handler = MessageHandler(self.client)
        
        logger.info("Bot initialized successfully")
    
    async def on_startup(self):
        """Actions to run on startup"""
        try:
            # Initialize database
            init_db()
            
            # Validate config
            Config.validate()
            
            # Start bot
            await self.client.start(bot_token=Config.BOT_TOKEN)
            logger.info("Bot is ready to serve!")
            
        except Exception as e:
            logger.error(f"Startup error: {e}")
            raise
    
    def register_handlers(self):
        """Register all message handlers"""
        
        @self.client.on(events.NewMessage(pattern='/start'))
        async def start_handler(event):
            await self.start_handler.handle(event)
        
        @self.client.on(events.NewMessage(pattern='/balance'))
        async def balance_handler(event):
            await self.balance_handler.show_balance(event)
        
        @self.client.on(events.CallbackQuery)
        async def callback_handler(event):
            await self.callback_handler.handle(event)
        
        @self.client.on(events.NewMessage)
        async def message_handler(event):
            await self.message_handler.handle_message(event)
    
    async def run_async(self):
        """Run bot asynchronously"""
        await self.on_startup()
        self.register_handlers()
        logger.info("Bot is running...")
        await self.client.run_until_disconnected()
    
    def run(self):
        """Run the bot"""
        # Start Flask server in background
        self._start_flask()
        
        # Run bot
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.run_async())
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Bot error: {e}")
        finally:
            loop.close()
    
    def _start_flask(self):
        """Start Flask server for health checks"""
        def run_flask():
            try:
                port = int(os.environ.get("PORT", 10000))
                app.run(host='0.0.0.0', port=port, debug=False)
            except Exception as e:
                logger.error(f"Flask server error: {e}")
        
        thread = threading.Thread(target=run_flask, daemon=True)
        thread.start()
        logger.info(f"Health check server starting on port {os.environ.get('PORT', 10000)}")

if __name__ == "__main__":
    bot = MoneyTrackerBot()
    bot.run()
