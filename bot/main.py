import os
import logging
import threading
import asyncio
from telethon import TelegramClient, events
from bot.config import Config
from bot.database.connection import init_db
from bot.utils.logger import setup_logger
from bot.handlers.start import StartHandler
from bot.handlers.balance import BalanceHandler
from bot.handlers.report import ReportHandler
from bot.handlers.history import HistoryHandler
from bot.handlers.debt import DebtHandler
from bot.handlers.goal import GoalHandler
from bot.handlers.wallet import WalletHandler
from bot.handlers.pdf import PDFHandler
from bot.handlers.transfer import TransferHandler
from bot.handlers.callback import CallbackHandler
from bot.handlers.message import MessageHandler
from bot.utils.temp_storage import temp_storage

# Setup logging
setup_logger()
logger = logging.getLogger(__name__)

class MoneyTrackerBot:
    """Main Bot Class"""
    
    def __init__(self):
        self.client = TelegramClient('bot_session', Config.API_ID, Config.API_HASH)
        
        # Initialize handlers
        self.start_handler = StartHandler(self.client)
        self.balance_handler = BalanceHandler(self.client)
        self.report_handler = ReportHandler(self.client)
        self.history_handler = HistoryHandler(self.client)
        self.debt_handler = DebtHandler(self.client)
        self.goal_handler = GoalHandler(self.client)
        self.wallet_handler = WalletHandler(self.client)
        self.pdf_handler = PDFHandler(self.client)
        self.transfer_handler = TransferHandler(self.client)
        self.callback_handler = CallbackHandler(self.client)
        self.message_handler = MessageHandler(self.client)
        
        logger.info("✅ Bot initialized successfully")
    
    async def on_startup(self):
        """Actions to run on startup"""
        try:
            # Initialize database
            init_db()
            
            # Validate config
            Config.validate()
            
            # Start bot
            await self.client.start(bot_token=Config.BOT_TOKEN)
            
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
        
        @self.client.on(events.NewMessage(pattern='/undo'))
        async def undo_handler(event):
            await self.message_handler.undo_last_entry(event)
        
        @self.client.on(events.NewMessage(pattern='/reset'))
        async def reset_handler(event):
            await self.message_handler.reset_data(event)
        
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
        logger.info("🤖 Bot is running...")
        await self.client.run_until_disconnected()
    
    def run(self):
        """Run the bot"""
        # Start health check server
        self._start_health_server()
        
        # Run bot
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.run_async())
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        finally:
            loop.close()
    
    def _start_health_server(self):
        """Start health check HTTP server for Render"""
        from http.server import HTTPServer, BaseHTTPRequestHandler
        
        class HealthCheckHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"""
                <!DOCTYPE html>
                <html>
                <head><title>Money Tracker Bot</title></head>
                <body>
                    <h1>✅ Money Tracker Bot is Online!</h1>
                    <p>Status: Running</p>
                    <p>Time: """ + str(datetime.now()).encode() + b"""</p>
                </body>
                </html>
                """)
            
            def do_HEAD(self):
                self.send_response(200)
                self.end_headers()
        
        def run_server():
            try:
                port = int(os.environ.get("PORT", 10000))
                server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
                logger.info(f"🌐 Health check server running on port {port}")
                server.serve_forever()
            except Exception as e:
                logger.error(f"Health server error: {e}")
        
        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()

if __name__ == "__main__":
    from datetime import datetime
    bot = MoneyTrackerBot()
    bot.run()
