"""
Report Handler Module
Handles /report command with today, date-wise, and monthly reports
"""

import math
import logging
from telethon import Button
from bot.handlers.base import BaseHandler
from bot.utils.translations import t
from bot.utils.helpers import get_current_month, get_current_date
from bot.database.repositories import BalanceRepository

logger = logging.getLogger(__name__)


class ReportHandler(BaseHandler):
    """
    Handler for /report command
    Shows today's report, date-wise report, and monthly summary
    """
    
    async def show_report_options(self, event):
        """
        Handle /report command - show report selection menu
        
        Args:
            event: Telegram event
        """
        user_id = event.sender_id
        
        buttons = [
            [Button.inline(t(user_id, 'today_income_expenses'), b"rep_today")],
            [Button.inline(t(user_id, 'date_wise'), b"rep_date")],
            [Button.inline(t(user_id, 'monthly_wise'), b"mrep_0")],
            [Button.inline(t(user_id, 'cancel'), b"cancel_state")]
        ]
        
        await event.respond(t(user_id, 'select_report'), buttons=buttons)
    
    async def show_today_report(self, event):
        """
        Show today's income and expense report
        
        Args:
            event: Telegram event
        """
        user_id = event.sender_id
        month_key = get_current_month(event)
        today = get_current_date(event)
        
        data = BalanceRepository.get_monthly_data(user_id, month_key)
        
        # Calculate today's totals
        today_income = 0.0
        today_expense = 0.0
        
        for entry in data['history']:
            if entry.get('date') == today:
                amt = entry.get('amount', 0)
                is_debt = entry.get('is_debt_logic', False)
                is_out_rep = entry.get('is_outstanding_repay', False)
                
                if not is_debt or is_out_rep:
                    if amt > 0:
                        today_income += amt
                    else:
                        today_expense += abs(amt)
        
        net = today_income - today_expense
        
        msg = (
            f"{t(user_id, 'today_report', today)}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"{t(user_id, 'total_income')}: {today_income:.2f}\n"
            f"{t(user_id, 'total_expense')}: {today_expense:.2f}\n"
            f"{t(user_id, 'net')}: {net:.2f}"
        )
        
        buttons = [[Button.inline(t(user_id, 'back'), b"rep_main")]]
        
        await event.edit(msg, buttons=buttons)
    
    async def show_date_wise_report(self, event, date):
        """
        Show report for a specific date
        
        Args:
            event: Telegram event
            date: Date in format DD-MM-YYYY
        """
        user_id = event.sender_id
        month_key = get_current_month(event)
        
        data = BalanceRepository.get_monthly_data(user_id, month_key)
        
        # Calculate totals for the date
        income = 0.0
        expense = 0.0
        
        for entry in data['history']:
            if entry.get('date') == date:
                amt = entry.get('amount', 0)
                is_debt = entry.get('is_debt_logic', False)
                is_out_rep = entry.get('is_outstanding_repay', False)
                
                if not is_debt or is_out_rep:
                    if amt > 0:
                        income += amt
                    else:
                        expense += abs(amt)
        
        net = income - expense
        
        msg = (
            f"{t(user_id, 'date_report', date)}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"{t(user_id, 'total_income')}: {income:.2f}\n"
            f"{t(user_id, 'total_expense')}: {expense:.2f}\n"
            f"{t(user_id, 'net')}: {net:.2f}"
        )
        
        buttons = [[Button.inline(t(user_id, 'back'), b"rep_main")]]
        
        await event.respond(msg, buttons=buttons)
    
    async def send_monthly_summary_page(self, user_id, chat_id, page_index, message_id=None):
        """
        Send monthly summary page with daily breakdown
        
        Args:
            user_id: User ID
            chat_id: Chat ID to send to
            page_index: Index of month to show (0 = latest)
            message_id: Optional message ID to edit
        """
        try:
            all_months = BalanceRepository.get_all_months(user_id)
            
            if not all_months:
                msg = t(user_id, 'no_data')
                if message_id:
                    try:
                        await self.client.edit_message(chat_id, message_id, msg)
                    except Exception as e:
                        logger.error(f"Edit failed for no_data: {e}")
                        await self.client.send_message(chat_id, msg)
                else:
                    await self.client.send_message(chat_id, msg)
                return
            
            # Sort months latest first
            all_months = all_months[::-1]
            total_months = len(all_months)
            
            # Ensure page_index is within bounds
            if page_index < 0:
                page_index = 0
            if page_index >= total_months:
                page_index = total_months - 1
            
            target = all_months[page_index]
            month_key = target.get('month', 'Unknown')
            history = target.get('history', [])
            
            total_inc = target.get('total_income', 0)
            total_exp = target.get('total_expense', 0)
            
            # Group by date
            daily_stats = {}
            for entry in history:
                d = entry.get('date', 'Unknown')
                amt = entry.get('amount', 0.0)
                
                if d not in daily_stats:
                    daily_stats[d] = {'inc': 0.0, 'exp': 0.0}
                
                # Skip debt entries that aren't repayments
                if entry.get("is_debt_logic") and not entry.get("is_outstanding_repay"):
                    continue
                
                if amt > 0:
                    daily_stats[d]['inc'] += amt
                else:
                    daily_stats[d]['exp'] += abs(amt)
            
            # Build message - ensure it's never empty
            month_title = t(user_id, 'monthly_report', month_key)
            msg_lines = [f"📅 **{month_title}**", "━━━━━━━━━━━━━━━━━━"]
            
            if not daily_stats:
                msg_lines.append(t(user_id, 'no_transactions'))
            else:
                for date in sorted(daily_stats.keys(), reverse=True):
                    stats = daily_stats[date]
                    net = stats['inc'] - stats['exp']
                    msg_lines.append(f"🗓 **{date}**")
                    msg_lines.append(f"{t(user_id, 'total_income')}: {stats['inc']:.0f} | "
                                    f"{t(user_id, 'total_expense')}: {stats['exp']:.0f} | "
                                    f"{t(user_id, 'net')}: {net:.0f}")
                    msg_lines.append("┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈")
            
            msg_lines.append(f"{t(user_id, 'total_income')}: {total_inc:.2f}")
            msg_lines.append(f"{t(user_id, 'total_expense')}: {total_exp:.2f}")
            msg_lines.append(f"{t(user_id, 'net')}: {total_inc - total_exp:.2f}")
            msg_lines.append(f"{t(user_id, 'page')}: {page_index + 1} / {total_months}")
            
            msg = "\n".join(msg_lines)
            
            # Build buttons safely
            buttons = []
            
            # Navigation buttons
            nav_buttons = []
            if page_index < total_months - 1:
                nav_buttons.append(Button.inline(t(user_id, 'previous'), f"mrep_{page_index + 1}"))
            if page_index > 0:
                nav_buttons.append(Button.inline(t(user_id, 'next'), f"mrep_{page_index - 1}"))
            
            if nav_buttons:
                buttons.append(nav_buttons)
            
            # Back button - always add
            back_button = Button.inline(t(user_id, 'back'), b"rep_main")
            buttons.append([back_button])
            
            # Send or edit message with proper error handling
            if message_id:
                try:
                    await self.client.edit_message(chat_id, message_id, msg, buttons=buttons)
                    logger.info(f"Successfully edited monthly report for user {user_id}, page {page_index}")
                except Exception as e:
                    logger.warning(f"Failed to edit message: {e}, sending new message")
                    try:
                        await self.client.send_message(chat_id, msg, buttons=buttons)
                    except Exception as e2:
                        logger.error(f"Failed to send with buttons: {e2}, sending without buttons")
                        await self.client.send_message(chat_id, msg)
            else:
                try:
                    await self.client.send_message(chat_id, msg, buttons=buttons)
                    logger.info(f"Successfully sent monthly report for user {user_id}, page {page_index}")
                except Exception as e:
                    logger.error(f"Failed to send with buttons: {e}, sending without buttons")
                    await self.client.send_message(chat_id, msg)
                    
        except Exception as e:
            logger.error(f"Unexpected error in send_monthly_summary_page: {e}", exc_info=True)
            try:
                error_msg = t(user_id, 'error_occurred')
                if message_id:
                    await self.client.edit_message(chat_id, message_id, error_msg)
                else:
                    await self.client.send_message(chat_id, error_msg)
            except:
                pass
