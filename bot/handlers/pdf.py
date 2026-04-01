"""
PDF Handler Module
Handles /pdf command for generating PDF reports
"""

import os
import logging
from telethon import Button
from bot.handlers.base import BaseHandler
from bot.utils.translations import t
from bot.utils.helpers import get_current_month, get_current_date
from bot.services.transaction_service import generate_pdf

logger = logging.getLogger(__name__)


class PDFHandler(BaseHandler):
    """
    Handler for /pdf command
    Generates PDF reports for current month, specific month, today, or specific date
    """
    
    async def show_pdf_options(self, event):
        """
        Handle /pdf command - show PDF options menu
        
        Args:
            event: Telegram event
        """
        user_id = event.sender_id
        
        buttons = [
            [Button.inline(t(user_id, 'pdf_current'), b"pdf_current")],
            [Button.inline(t(user_id, 'pdf_month_wise'), b"pdf_month_wise")],
            [Button.inline(t(user_id, 'pdf_today'), b"pdf_today")],
            [Button.inline(t(user_id, 'pdf_date_wise'), b"pdf_date_wise")],
            [Button.inline(t(user_id, 'cancel'), b"cancel_state")]
        ]
        
        await event.respond(t(user_id, 'pdf_options'), buttons=buttons, parse_mode=None)
    
    async def generate_current_month_pdf(self, event):
        """
        Generate PDF for current month
        
        Args:
            event: Telegram event
        """
        user_id = event.sender_id
        month_key = get_current_month(event)
        
        file = generate_pdf(user_id, month_key, title_suffix=f"Full {month_key}")
        
        if file:
            await self.client.send_file(
                event.chat_id,
                file,
                caption=t(user_id, 'pdf_sent', month_key)
            )
            os.remove(file)
        else:
            await event.answer(t(user_id, 'no_data'), alert=True)
    
    async def prompt_month_for_pdf(self, event):
        """
        Show prompt for month input (e.g., Jan-2026)
        
        Args:
            event: Telegram event
        """
        user_id = event.sender_id
        
        # Set state in MessageHandler's user_states (shared)
        from bot.handlers.message import MessageHandler
        MessageHandler.user_states[user_id] = "ST_PDF_MONTH"
        
        logger.info(f"User {user_id} set to ST_PDF_MONTH state")
        
        await event.edit(
            t(user_id, 'pdf_month_prompt'),
            buttons=[Button.inline(t(user_id, 'back'), b"pdf_main")],
            parse_mode=None
        )
    
    async def generate_month_pdf(self, user_id, chat_id, month_input):
        """
        Generate PDF for a specific month
        
        Args:
            user_id: User ID
            chat_id: Chat ID to send to
            month_input: Month in format "Jan-2026"
        """
        try:
            logger.info(f"Generating PDF for month: {month_input}, user: {user_id}")
            
            # Validate month format
            from datetime import datetime
            try:
                datetime.strptime(month_input, "%b-%Y")
            except ValueError:
                await self.client.send_message(
                    chat_id, 
                    "❌ ভুল ফরম্যাট! মাস-বছর লিখুন (যেমন: Jan-2026)",
                    parse_mode=None
                )
                return
            
            file = generate_pdf(user_id, month_input, title_suffix=month_input)
            
            if file and os.path.exists(file):
                await self.client.send_file(
                    chat_id,
                    file,
                    caption=t(user_id, 'pdf_sent', month_input),
                    parse_mode=None
                )
                os.remove(file)
                logger.info(f"PDF sent successfully for month: {month_input}")
            else:
                await self.client.send_message(
                    chat_id, 
                    t(user_id, 'pdf_no_data_month'),
                    parse_mode=None
                )
        except Exception as e:
            logger.error(f"Error generating month PDF: {e}")
            await self.client.send_message(
                chat_id,
                "❌ PDF জেনারেট করতে সমস্যা হয়েছে।",
                parse_mode=None
            )
    
    async def generate_today_pdf(self, event):
        """
        Generate PDF for today's transactions
        
        Args:
            event: Telegram event
        """
        user_id = event.sender_id
        month_key = get_current_month(event)
        today = get_current_date(event)
        
        file = generate_pdf(
            user_id,
            month_key,
            history_filter=today,
            title_suffix=f"Today ({today})"
        )
        
        if file:
            await self.client.send_file(
                event.chat_id,
                file,
                caption=t(user_id, 'pdf_today_sent', today)
            )
            os.remove(file)
        else:
            await event.answer(t(user_id, 'pdf_no_data'), alert=True)
    
    async def prompt_date_for_pdf(self, event):
        """
        Show prompt for date input (DD-MM-YYYY)
        
        Args:
            event: Telegram event
        """
        user_id = event.sender_id
        
        # Set state in MessageHandler's user_states (shared)
        from bot.handlers.message import MessageHandler
        MessageHandler.user_states[user_id] = "ST_PDF_DATE"
        
        logger.info(f"User {user_id} set to ST_PDF_DATE state")
        
        await event.edit(
            t(user_id, 'pdf_date_prompt'),
            buttons=[Button.inline(t(user_id, 'back'), b"pdf_main")],
            parse_mode=None
        )
    
    async def generate_date_pdf(self, user_id, chat_id, date_input):
        """
        Generate PDF for a specific date
        
        Args:
            user_id: User ID
            chat_id: Chat ID to send to
            date_input: Date in format "DD-MM-YYYY"
        """
        try:
            logger.info(f"Generating PDF for date: {date_input}, user: {user_id}")
            
            # Validate date format
            from datetime import datetime
            try:
                datetime.strptime(date_input, "%d-%m-%Y")
            except ValueError:
                await self.client.send_message(
                    chat_id,
                    "❌ ভুল ফরম্যাট! তারিখ লিখুন (যেমন: 01-01-2026)",
                    parse_mode=None
                )
                return
            
            month_key = get_current_month()
            
            file = generate_pdf(
                user_id,
                month_key,
                history_filter=date_input,
                title_suffix=f"Date ({date_input})"
            )
            
            if file and os.path.exists(file):
                await self.client.send_file(
                    chat_id,
                    file,
                    caption=t(user_id, 'pdf_today_sent', date_input),
                    parse_mode=None
                )
                os.remove(file)
                logger.info(f"PDF sent successfully for date: {date_input}")
            else:
                await self.client.send_message(
                    chat_id,
                    t(user_id, 'pdf_no_data'),
                    parse_mode=None
                )
        except Exception as e:
            logger.error(f"Error generating date PDF: {e}")
            await self.client.send_message(
                chat_id,
                "❌ PDF জেনারেট করতে সমস্যা হয়েছে।",
                parse_mode=None
            )
    
    def clear_user_state(self, user_id):
        """
        Clear user state from MessageHandler's user_states
        
        Args:
            user_id: User ID
        """
        from bot.handlers.message import MessageHandler
        MessageHandler.user_states.pop(user_id, None)
    
    def is_valid_month(self, month_str):
        """
        Check if month string is valid (Jan-2026 format)
        
        Args:
            month_str: Month string to validate
            
        Returns:
            bool: True if valid
        """
        from datetime import datetime
        try:
            datetime.strptime(month_str, "%b-%Y")
            return True
        except ValueError:
            return False
    
    def is_valid_date(self, date_str):
        """
        Check if date string is valid (DD-MM-YYYY format)
        
        Args:
            date_str: Date string to validate
            
        Returns:
            bool: True if valid
        """
        from datetime import datetime
        try:
            datetime.strptime(date_str, "%d-%m-%Y")
            return True
        except ValueError:
            return False
