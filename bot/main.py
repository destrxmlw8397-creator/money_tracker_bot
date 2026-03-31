import logging
import threading
from telethon import TelegramClient, events
from bot.config import Config
from bot.database.connection import init_db
from bot.utils.logger import setup_logger
from bot.handlers.start import StartHandler
from bot.handlers.balance import BalanceHandler
from bot.handlers.callback import CallbackHandler
from bot.utils.temp_storage import temp_storage
import asyncio

# Setup logging
setup_logger()
logger = logging.getLogger(__name__)

class MoneyTrackerBot:
    """Main Bot Class"""
    
    def __init__(self):
        self.client = TelegramClient('bot_session', Config.API_ID, Config.API_HASH)
        self.client.start(bot_token=Config.BOT_TOKEN)
        
        # Initialize handlers
        self.start_handler = StartHandler(self.client)
        self.balance_handler = BalanceHandler(self.client)
        self.callback_handler = CallbackHandler(self.client)
        
        logger.info("✅ Bot initialized successfully")
    
    async def on_startup(self):
        """Actions to run on startup"""
        try:
            # Initialize database
            init_db()
            
            # Validate config
            Config.validate()
            
            logger.info("🚀 Bot is ready to serve!")
        except Exception as e:
            logger.error(f"Startup error: {e}")
            raise
    
    def register_handlers(self):
        """Register all message handlers"""
        
        @self.client.on(events.NewMessage(pattern='/start'))
        async def start_handler(event):
            await self.start_handler.handle(event)
        
        @self.client.on(events.NewMessage(pattern='/lang'))
        async def lang_handler(event):
            await self.start_handler.handle_language(event)
        
        @self.client.on(events.NewMessage(pattern='/balance'))
        async def balance_handler(event):
            await self.balance_handler.show_balance(event)
        
        # Add all other command handlers here...
        # (Similar pattern for /debt, /goal, /pdf, etc.)
        
        @self.client.on(events.CallbackQuery)
        async def callback_handler(event):
            await self.callback_handler.handle(event)
        
        @self.client.on(events.NewMessage)
        async def message_handler(event):
            await self.callback_handler.handle_message(event)
    
    def run(self):
        """Run the bot"""
        # Run startup in event loop
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.on_startup())
        
        # Register handlers
        self.register_handlers()
        
        # Start health check server
        self._start_health_server()
        
        logger.info("🤖 Bot is running...")
        self.client.run_until_disconnected()
    
    def _start_health_server(self):
        """Start health check HTTP server"""
        from http.server import HTTPServer, BaseHTTPRequestHandler
        
        class HealthCheckHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Money Tracker Pro is Online!")
            
            def do_HEAD(self):
                self.send_response(200)
                self.end_headers()
        
        def run_server():
            try:
                server = HTTPServer(('0.0.0.0', Config.PORT), HealthCheckHandler)
                server.serve_forever()
            except Exception:
                pass
        
        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()
        logger.info(f"Health check server started on port {Config.PORT}")

if __name__ == "__main__":
    bot = MoneyTrackerBot()
    bot.run()
