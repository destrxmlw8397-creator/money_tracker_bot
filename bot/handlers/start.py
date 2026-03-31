from bot.handlers.base import BaseHandler
from bot.utils.translations import t
from bot.utils.helpers import get_current_month
from telethon import Button

class StartHandler(BaseHandler):
    async def handle(self, event):
        user_id = event.sender_id
        await event.respond(t(user_id, 'welcome', get_current_month(event)))
    
    async def handle_language(self, event):
        user_id = event.sender_id
        buttons = [
            [Button.inline(t(user_id, 'lang_bn'), b"lang_bn")],
            [Button.inline(t(user_id, 'lang_en'), b"lang_en")],
            [Button.inline(t(user_id, 'cancel'), b"cancel_state")]
        ]
        await event.respond(t(user_id, 'select_language'), buttons=buttons)
