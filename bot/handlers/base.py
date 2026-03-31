from telethon import Button
from bot.utils.translations import t
import logging

logger = logging.getLogger(__name__)

class BaseHandler:
    def __init__(self, client):
        self.client = client
    
    async def send_message(self, user_id, chat_id, key, *args, **kwargs):
        text = t(user_id, key, *args)
        await self.client.send_message(chat_id, text, **kwargs)
    
    async def edit_message(self, message, user_id, key, *args, **kwargs):
        text = t(user_id, key, *args)
        await self.client.edit_message(message.chat_id, message.id, text, **kwargs)
