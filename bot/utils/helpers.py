from datetime import datetime, timedelta, timezone
from bot.config import Config

def get_user_now(event=None):
    tz_offset = timezone(timedelta(hours=6))
    now = datetime.now(tz_offset)
    if event and hasattr(event, 'message') and event.message and event.message.date:
        return event.message.date.astimezone(tz_offset)
    return now

def get_current_month(event=None):
    return get_user_now(event).strftime("%b-%Y")

def get_current_date(event=None):
    return get_user_now(event).strftime("%d-%m-%Y")

def get_current_time(event=None):
    return get_user_now(event).strftime("%H:%M")
