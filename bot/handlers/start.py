from bot.handlers.base import BaseHandler
from bot.utils.translations import t
from bot.utils.helpers import get_current_month
from telethon import Button

class StartHandler(BaseHandler):
    """Handler for /start command"""
    
    async def handle(self, event):
        """Handle /start command"""
        user_id = event.sender_id
        welcome_text = t(user_id, 'welcome', get_current_month())
        await event.respond(welcome_text)
    
    async def handle_language(self, event):
        """Handle language selection"""
        user_id = event.sender_id
        buttons = [
            [Button.inline(t(user_id, 'lang_bn'), b"lang_bn")],
            [Button.inline(t(user_id, 'lang_en'), b"lang_en")],
            [Button.inline(t(user_id, 'cancel'), b"cancel_state")]
        ]
        await event.respond(t(user_id, 'select_language'), buttons=buttons)
