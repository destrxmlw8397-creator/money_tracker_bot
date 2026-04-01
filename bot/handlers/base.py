"""
Base Handler Module
Provides base class for all handlers with common functionality
"""

import logging
from telethon import Button
from bot.utils.translations import t

logger = logging.getLogger(__name__)


class BaseHandler:
    """
    Base handler class that all other handlers inherit from
    
    Provides common methods for sending and editing messages with translations
    """
    
    def __init__(self, client):
        """
        Initialize base handler
        
        Args:
            client: Telethon client instance
        """
        self.client = client
    
    async def send_message(self, user_id, chat_id, key, *args, **kwargs):
        """
        Send a translated message
        
        Args:
            user_id: User ID for language selection
            chat_id: Chat ID to send to
            key: Translation key
            *args: Format arguments for translation
            **kwargs: Additional arguments for send_message
        """
        text = t(user_id, key, *args)
        await self.client.send_message(chat_id, text, **kwargs)
    
    async def edit_message(self, message, user_id, key, *args, **kwargs):
        """
        Edit an existing message with translated text
        
        Args:
            message: Message object to edit
            user_id: User ID for language selection
            key: Translation key
            *args: Format arguments for translation
            **kwargs: Additional arguments for edit_message
        """
        text = t(user_id, key, *args)
        await self.client.edit_message(message.chat_id, message.id, text, **kwargs)
    
    async def respond_with_back_button(self, event, user_id, key, back_callback, *args):
        """
        Respond with a message and a back button
        
        Args:
            event: Telegram event
            user_id: User ID for language selection
            key: Translation key
            back_callback: Callback data for back button
            *args: Format arguments for translation
        """
        text = t(user_id, key, *args)
        buttons = [[Button.inline(t(user_id, 'back'), back_callback)]]
        await event.respond(text, buttons=buttons)
    
    def log_error(self, error, context=None):
        """
        Log an error with context
        
        Args:
            error: Exception object
            context: Additional context information
        """
        logger.error(f"Error in {self.__class__.__name__}: {error}", exc_info=True)
        if context:
            logger.error(f"Context: {context}")
