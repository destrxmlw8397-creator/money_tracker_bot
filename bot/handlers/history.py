"""
History Handler Module
Handles /history command with pagination for transaction history
"""

import math
from telethon import Button
from bot.handlers.base import BaseHandler
from bot.utils.translations import t
from bot.utils.helpers import get_current_month
from bot.database.repositories import BalanceRepository


class HistoryHandler(BaseHandler):
    """
    Handler for /history command
    Shows transaction history with pagination (10 items per page)
    """
    
    async def show_history(self, event):
        """
        Handle /history command - show first page of history
        
        Args:
            event: Telegram event
        """
        await self.send_history_page(event.sender_id, event.chat_id, 0)
    
    async def send_history_page(self, user_id, chat_id, page, message_id=None):
        """
        Send history page with pagination
        
        Args:
            user_id: User ID
            chat_id: Chat ID to send to
            page: Page number (0-based)
            message_id: Optional message ID to edit instead of send new
        """
        month_key = get_current_month()
        data = BalanceRepository.get_monthly_data(user_id, month_key)
        
        if not data or not data.get('history'):
            await self.client.send_message(chat_id, t(user_id, 'no_history'))
            return
        
        # Get history in reverse order (latest first)
        full_history = data['history'][::-1]
        page_size = 10
        total_pages = math.ceil(len(full_history) / page_size)
        
        # Ensure page is within bounds
        if page < 0:
            page = 0
        if page >= total_pages:
            page = total_pages - 1
        
        start_idx = page * page_size
        end_idx = start_idx + page_size
        history_slice = full_history[start_idx:end_idx]
        
        # Build message
        msg = f"{t(user_id, 'detailed_history', month_key)}\n"
        msg += f"━━━━━━━━━━━━━━━━━━\n"
        msg += f"{t(user_id, 'page')}: {page + 1} / {total_pages}\n\n"
        
        for entry in history_slice:
            icon = "💰" if entry['amount'] > 0 else "💸"
            wallet = entry.get('wallet', 'Cash')
            category = entry.get('category', 'General')
            date = entry.get('date', '')
            amount = entry['amount']
            
            msg += f"{icon} {amount:+.2f} | {category} | {wallet} | {date}\n"
        
        # Create pagination buttons
        buttons = []
        nav_row = []
        
        if page > 0:
            nav_row.append(Button.inline(t(user_id, 'previous'), f"hist_{page - 1}"))
        if page < total_pages - 1:
            nav_row.append(Button.inline(t(user_id, 'next'), f"hist_{page + 1}"))
        
        if nav_row:
            buttons.append(nav_row)
        
        buttons.append([Button.inline(t(user_id, 'cancel'), b"cancel_state")])
        
        # Send or edit message
        if message_id:
            await self.client.edit_message(chat_id, message_id, msg, buttons=buttons)
        else:
            await self.client.send_message(chat_id, msg, buttons=buttons)
    
    async def get_total_pages(self, user_id):
        """
        Get total number of history pages
        
        Args:
            user_id: User ID
            
        Returns:
            int: Total number of pages
        """
        month_key = get_current_month()
        data = BalanceRepository.get_monthly_data(user_id, month_key)
        
        if not data or not data.get('history'):
            return 0
        
        return math.ceil(len(data['history']) / 10)
