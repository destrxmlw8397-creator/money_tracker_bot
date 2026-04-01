"""
Helpers Module
Contains utility functions for date/time handling and common operations
"""

from datetime import datetime, timedelta, timezone
from bot.config import Config


def get_user_now(event=None):
    """
    Get current time in Bangladesh timezone (UTC+6)
    
    Args:
        event: Optional Telegram event to get message time from
        
    Returns:
        datetime: Current time in UTC+6 timezone
    """
    tz_offset = timezone(timedelta(hours=6))
    now = datetime.now(tz_offset)
    
    if event and hasattr(event, 'message') and event.message and event.message.date:
        return event.message.date.astimezone(tz_offset)
    
    return now


def get_current_month(event=None):
    """
    Get current month in format "Jan-2026"
    
    Args:
        event: Optional Telegram event
        
    Returns:
        str: Current month in format "Jan-2026"
    """
    return get_user_now(event).strftime("%b-%Y")


def get_current_date(event=None):
    """
    Get current date in format "DD-MM-YYYY"
    
    Args:
        event: Optional Telegram event
        
    Returns:
        str: Current date in format "DD-MM-YYYY"
    """
    return get_user_now(event).strftime("%d-%m-%Y")


def get_current_time(event=None):
    """
    Get current time in format "HH:MM"
    
    Args:
        event: Optional Telegram event
        
    Returns:
        str: Current time in format "HH:MM"
    """
    return get_user_now(event).strftime("%H:%M")


def get_current_time_12hr(event=None):
    """
    Get current time in 12-hour format with AM/PM
    
    Args:
        event: Optional Telegram event
        
    Returns:
        str: Current time in format "HH:MM AM/PM"
    """
    return get_user_now(event).strftime("%I:%M %p")


def format_amount(amount):
    """
    Format amount with proper sign and decimal places
    
    Args:
        amount: Float amount
        
    Returns:
        str: Formatted amount string
    """
    if amount > 0:
        return f"+{amount:.2f}"
    return f"{amount:.2f}"


def parse_amount(text):
    """
    Extract amount from text
    
    Args:
        text: Input text containing amount
        
    Returns:
        float: Extracted amount or None
    """
    import re
    match = re.search(r'([-+]?\d*\.?\d+)', text)
    if match:
        return float(match.group(1))
    return None


def extract_wallet_and_category(text, available_wallets):
    """
    Extract wallet name and category from input text
    
    Args:
        text: Input text
        available_wallets: Dictionary of available wallets
        
    Returns:
        tuple: (wallet_name, category)
    """
    import re
    
    wallet = "Cash"
    for w in available_wallets.keys():
        if w.lower() in text.lower():
            wallet = w
            break
    
    # Remove wallet names and amount to get category
    pattern = '|'.join(map(re.escape, available_wallets.keys()))
    category = re.sub(pattern, '', text, flags=re.I)
    category = re.sub(r'[-+]?\d*\.?\d+', '', category).strip()
    
    if not category:
        category = "General"
    
    return wallet, category


def calculate_age_in_months(start_month, end_month=None):
    """
    Calculate number of months between two months
    
    Args:
        start_month: Start month in format "Jan-2026"
        end_month: End month in format "Jan-2026" (defaults to current)
        
    Returns:
        int: Number of months difference
    """
    if end_month is None:
        end_month = get_current_month()
    
    start = datetime.strptime(start_month, "%b-%Y")
    end = datetime.strptime(end_month, "%b-%Y")
    
    return (end.year - start.year) * 12 + (end.month - start.month)


def is_valid_month(month_str):
    """
    Check if month string is valid
    
    Args:
        month_str: Month in format "Jan-2026"
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        datetime.strptime(month_str, "%b-%Y")
        return True
    except ValueError:
        return False


def is_valid_date(date_str):
    """
    Check if date string is valid in format DD-MM-YYYY
    
    Args:
        date_str: Date in format "DD-MM-YYYY"
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        datetime.strptime(date_str, "%d-%m-%Y")
        return True
    except ValueError:
        return False


def get_month_name(month_num):
    """
    Get month name from month number
    
    Args:
        month_num: Month number (1-12)
        
    Returns:
        str: Month name (e.g., "Jan")
    """
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    return months[month_num - 1] if 1 <= month_num <= 12 else "Jan"


def get_next_month(current_month):
    """
    Get next month string
    
    Args:
        current_month: Current month in format "Jan-2026"
        
    Returns:
        str: Next month in format "Feb-2026"
    """
    date = datetime.strptime(current_month, "%b-%Y")
    if date.month == 12:
        next_date = date.replace(year=date.year + 1, month=1)
    else:
        next_date = date.replace(month=date.month + 1)
    return next_date.strftime("%b-%Y")


def get_previous_month(current_month):
    """
    Get previous month string
    
    Args:
        current_month: Current month in format "Jan-2026"
        
    Returns:
        str: Previous month in format "Dec-2025"
    """
    date = datetime.strptime(current_month, "%b-%Y")
    if date.month == 1:
        prev_date = date.replace(year=date.year - 1, month=12)
    else:
        prev_date = date.replace(month=date.month - 1)
    return prev_date.strftime("%b-%Y")
