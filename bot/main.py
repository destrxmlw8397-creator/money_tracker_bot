"""
Money Tracker Bot - Main Entry Point
PostgreSQL Version with Complete Features
"""

import os
import logging
import threading
import asyncio
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
from bot.config import Config
from bot.database.connection import init_db
from bot.utils.translations import t
from bot.utils.helpers import get_current_month
from bot.handlers.start import StartHandler
from bot.handlers.balance import BalanceHandler
from bot.handlers.report import ReportHandler
from bot.handlers.history import HistoryHandler
from bot.handlers.debt import DebtHandler
from bot.handlers.goal import GoalHandler
from bot.handlers.transfer import TransferHandler
from bot.handlers.pdf import PDFHandler
from bot.handlers.wallet import WalletHandler
from bot.handlers.callback import CallbackHandler
from bot.handlers.message import MessageHandler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HealthCheckHandler(BaseHTTPRequestHandler):
    """Simple health check handler for Render"""
    
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Money Tracker Pro is Online!")
    
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()


def run_health_server():
    """Run health check server in background thread"""
    try:
        port = Config.PORT
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        logger.info(f"🌐 Health check server running on port {port}")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Health server error: {e}")


class MoneyTrackerBot:
    """Main Bot Class"""
    
    def __init__(self):
        """Initialize bot and all handlers"""
        self.client = TelegramClient('bot_session', Config.API_ID, Config.API_HASH)
        
        # Initialize all handlers
        self.start_handler = StartHandler(self.client)
        self.balance_handler = BalanceHandler(self.client)
        self.report_handler = ReportHandler(self.client)
        self.history_handler = HistoryHandler(self.client)
        self.debt_handler = DebtHandler(self.client)
        self.goal_handler = GoalHandler(self.client)
        self.transfer_handler = TransferHandler(self.client)
        self.pdf_handler = PDFHandler(self.client)
        self.wallet_handler = WalletHandler(self.client)
        self.callback_handler = CallbackHandler(self.client)
        self.message_handler = MessageHandler(self.client)
        
        logger.info("✅ Bot initialized successfully")
    
    async def on_startup(self):
        """Actions to run on startup"""
        try:
            # Initialize database tables
            init_db()
            
            # Validate configuration
            Config.validate()
            
            # Start bot client
            await self.client.start(bot_token=Config.BOT_TOKEN)
            
            logger.info("🚀 Bot is ready to serve!")
            
        except Exception as e:
            logger.error(f"Startup error: {e}")
            raise
    
    def register_handlers(self):
        """Register all message and callback handlers"""
        
        @self.client.on(events.NewMessage(pattern='/start'))
        async def start_handler(event):
            await self.start_handler.handle(event)
        
        @self.client.on(events.NewMessage(pattern='/lang'))
        async def lang_handler(event):
            await self.start_handler.handle_language(event)
        
        @self.client.on(events.NewMessage(pattern='/balance'))
        async def balance_handler(event):
            await self.balance_handler.show_balance(event)
        
        @self.client.on(events.NewMessage(pattern='/report'))
        async def report_handler(event):
            await self.report_handler.show_report_options(event)
        
        @self.client.on(events.NewMessage(pattern='/history'))
        async def history_handler(event):
            await self.history_handler.show_history(event)
        
        @self.client.on(events.NewMessage(pattern='/debt'))
        async def debt_handler(event):
            await self.debt_handler.show_debt_menu(event)
        
        @self.client.on(events.NewMessage(pattern='/goal'))
        async def goal_handler(event):
            await self.goal_handler.show_goal_menu(event)
        
        @self.client.on(events.NewMessage(pattern='/trns_money'))
        async def transfer_handler(event):
            await self.transfer_handler.start_transfer(event)
        
        @self.client.on(events.NewMessage(pattern='/pdf'))
        async def pdf_handler(event):
            await self.pdf_handler.show_pdf_options(event)
        
        @self.client.on(events.NewMessage(pattern='/setbudget'))
        async def set_budget_handler(event):
            await self.wallet_handler.set_budget(event)
        
        @self.client.on(events.NewMessage(pattern='/addwallet'))
        async def add_wallet_handler(event):
            await self.wallet_handler.add_wallet(event)
        
        @self.client.on(events.NewMessage(pattern='/delwallet'))
        async def delete_wallet_handler(event):
            await self.wallet_handler.delete_wallet(event)
        
        # ========== FIX: Removed duplicate /undo and /reset handlers ==========
        # /undo and /reset are now handled only by the generic message handler below
        # This prevents double processing of these commands
        
        @self.client.on(events.CallbackQuery)
        async def callback_handler(event):
            await self.callback_handler.handle(event)
        
        # Generic message handler - handles all messages including /undo and /reset
        @self.client.on(events.NewMessage)
        async def message_handler(event):
            await self.message_handler.handle_message(event)
    
    async def run_async(self):
        """Run bot asynchronously"""
        await self.on_startup()
        self.register_handlers()
        logger.info("🤖 Bot is running...")
        await self.client.run_until_disconnected()
    
    def run(self):
        """Run the bot"""
        # Start health check server in background
        threading.Thread(target=run_health_server, daemon=True).start()
        
        # Run bot
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.run_async())
        except KeyboardInterrupt:
            logger.info("🛑 Bot stopped by user")
        except Exception as e:
            logger.error(f"❌ Bot error: {e}")
        finally:
            loop.close()


if __name__ == "__main__":
    bot = MoneyTrackerBot()
    bot.run()
