import math
from bot.handlers.base import BaseHandler
from bot.utils.translations import t
from bot.utils.helpers import get_current_month
from bot.database.repositories import BalanceRepository
from telethon import Button

class HistoryHandler(BaseHandler):
    async def show_history(self, event):
        await self.send_history_page(event.sender_id, event.chat_id, 0)
    
    async def send_history_page(self, user_id, chat_id, page, message_id=None):
        month_key = get_current_month()
        data = BalanceRepository.get_monthly_data(user_id, month_key)
        
        if not data or not data.get('history'):
            await self.client.send_message(chat_id, t(user_id, 'no_history'))
            return
        
        full_history = data['history'][::-1]
        page_size = 10
        total_pages = math.ceil(len(full_history) / page_size)
        
        start = page * page_size
        end = start + page_size
        history_slice = full_history[start:end]
        
        msg = f"{t(user_id, 'detailed_history', month_key)}\n━━━━━━━━━━━━━━━━━━\n"
        msg += f"{t(user_id, 'page')}: {page + 1} / {total_pages}\n\n"
        
        for entry in history_slice:
            icon = "💰" if entry['amount'] > 0 else "💸"
            wallet = entry.get('wallet', 'Cash')
            msg += f"{icon} {entry['amount']} | {entry['category']} | {wallet} | {entry.get('date', '')}\n"
        
        buttons = []
        nav = []
        if page > 0:
            nav.append(Button.inline(t(user_id, 'previous'), f"hist_{page-1}"))
        if page < total_pages - 1:
            nav.append(Button.inline(t(user_id, 'next'), f"hist_{page+1}"))
        if nav:
            buttons.append(nav)
        buttons.append([Button.inline(t(user_id, 'cancel'), b"cancel_state")])
        
        if message_id:
            await self.client.edit_message(chat_id, message_id, msg, buttons=buttons or None)
        else:
            await self.client.send_message(chat_id, msg, buttons=buttons or None)
