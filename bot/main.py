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
from bot.handlers.callback import CallbackHandler
from bot.handlers.message import MessageHandler
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Money Tracker Pro is Online!")
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_health_server():
    try:
        port = Config.PORT
        server = HTTPServer(('0.0.0.0', port), HealthHandler)
        server.serve_forever()
    except Exception as e:
        logger.error(f"Health server error: {e}")

class MoneyTrackerBot:
    def __init__(self):
        self.client = TelegramClient('bot_session', Config.API_ID, Config.API_HASH)
        self.start_handler = StartHandler(self.client)
        self.balance_handler = BalanceHandler(self.client)
        self.callback_handler = CallbackHandler(self.client)
        self.message_handler = MessageHandler(self.client)
        logger.info("Bot initialized")
    
    async def on_startup(self):
        try:
            init_db()
            Config.validate()
            await self.client.start(bot_token=Config.BOT_TOKEN)
            logger.info("Bot ready to serve!")
        except Exception as e:
            logger.error(f"Startup error: {e}")
            raise
    
    def register_handlers(self):
        @self.client.on(events.NewMessage(pattern='/start'))
        async def start_handler(event):
            await self.start_handler.handle(event)
        
        @self.client.on(events.NewMessage(pattern='/lang'))
        async def lang_handler(event):
            await self.start_handler.handle_language(event)
        
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
        await self.on_startup()
        self.register_handlers()
        logger.info("Bot running...")
        await self.client.run_until_disconnected()
    
    def run(self):
        threading.Thread(target=run_health_server, daemon=True).start()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.run_async())
        except KeyboardInterrupt:
            logger.info("Bot stopped")
        except Exception as e:
            logger.error(f"Bot error: {e}")
        finally:
            loop.close()

if __name__ == "__main__":
    bot = MoneyTrackerBot()
    bot.run()
