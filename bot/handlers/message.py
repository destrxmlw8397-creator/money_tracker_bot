# bot/handlers/message.py
from telethon import events
from bot.handlers.base import BaseHandler

class MessageHandler(BaseHandler):
    """Handle regular messages"""
    
    async def handle_message(self, event):
        """Handle incoming messages"""
        # আপনার মেসেজ হ্যান্ডলিং কোড এখানে
        # যেমন: /undo, /reset, এবং সাধারণ ইনপুট প্রসেসিং
        
        text = event.text.strip()
        
        if text.startswith('/undo'):
            # undo লজিক
            pass
        elif text.startswith('/reset'):
            # reset লজিক
            pass
        else:
            # সাধারণ ট্রানজেকশন প্রসেসিং
            pass
