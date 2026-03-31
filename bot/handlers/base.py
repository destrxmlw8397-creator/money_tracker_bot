from telethon import events, Button
from bot.utils.translations import t
import logging

logger = logging.getLogger(__name__)

class BaseHandler:
    """Base handler class - all handlers inherit from this"""
    
    def __init__(self, client):
        self.client = client
    
    async def send_message(self, user_id: int, chat_id: int, key: str, *args, **kwargs):
        """Send translated message"""
        text = t(user_id, key, *args)
        await self.client.send_message(chat_id, text, **kwargs)
    
    async def edit_message(self, message, user_id: int, key: str, *args, **kwargs):
        """Edit message with translation"""
        text = t(user_id, key, *args)
        await self.client.edit_message(message.chat_id, message.id, text, **kwargs)
    
    async def respond_with_back_button(self, event, user_id: int, key: str, back_callback: str, *args):
        """Respond with message and back button"""
        text = t(user_id, key, *args)
        buttons = [[Button.inline(t(user_id, 'back'), back_callback)]]
        await event.respond(text, buttons=buttons)
    
    def log_error(self, error: Exception, context: str = None):
        """Log error with context"""
        logger.error(f"Error in {self.__class__.__name__}: {error}", exc_info=True)
        if context:
            logger.error(f"Context: {context}")
