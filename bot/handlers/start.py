"""
Start Handler Module
Handles /start and /lang commands
"""

from telethon import Button
from bot.handlers.base import BaseHandler
from bot.utils.translations import t, set_user_lang
from bot.utils.helpers import get_current_month


class StartHandler(BaseHandler):
    """
    Handler for /start and /lang commands
    """
    
    async def handle(self, event):
        """
        Handle /start command
        
        Args:
            event: Telegram event
        """
        user_id = event.sender_id
        welcome_text = t(user_id, 'welcome', get_current_month(event))
        await event.respond(welcome_text)
    
    async def handle_language(self, event):
        """
        Handle /lang command - show language selection menu
        
        Args:
            event: Telegram event
        """
        user_id = event.sender_id
        
        buttons = [
            [Button.inline(t(user_id, 'lang_bn'), b"lang_bn")],
            [Button.inline(t(user_id, 'lang_en'), b"lang_en")],
            [Button.inline(t(user_id, 'cancel'), b"cancel_state")]
        ]
        
        await event.respond(t(user_id, 'select_language'), buttons=buttons)
    
    async def set_language(self, event, lang):
        """
        Set user language preference
        
        Args:
            event: Telegram event
            lang: Language code ('bn' or 'en')
        """
        user_id = event.sender_id
        set_user_lang(user_id, lang)
        
        language_name = 'বাংলা' if lang == 'bn' else 'English'
        await event.edit(t(user_id, 'language_set', language_name))
