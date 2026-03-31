from bot.handlers.base import BaseHandler
from bot.utils.translations import t
from bot.utils.helpers import get_current_month, get_current_date
from bot.services.transaction_service import generate_pdf
from telethon import Button
import os

class PDFHandler(BaseHandler):
    user_states = {}
    
    async def show_pdf_options(self, event):
        user_id = event.sender_id
        buttons = [
            [Button.inline(t(user_id, 'pdf_current'), b"pdf_current")],
            [Button.inline(t(user_id, 'pdf_month_wise'), b"pdf_month_wise")],
            [Button.inline(t(user_id, 'pdf_today'), b"pdf_today")],
            [Button.inline(t(user_id, 'pdf_date_wise'), b"pdf_date_wise")],
            [Button.inline(t(user_id, 'cancel'), b"cancel_state")]
        ]
        await event.respond(t(user_id, 'pdf_options'), buttons=buttons)
