# bot/utils/error_handler.py
import traceback
import logging

logger = logging.getLogger(__name__)

async def handle_bot_error(error, context=None):
    """Handle bot errors gracefully"""
    error_msg = f"Error: {error}\n{traceback.format_exc()}"
    logger.error(error_msg)
    
    if context and hasattr(context, 'event'):
        try:
            await context.event.respond(
                "❌ একটি ত্রুটি ঘটেছে। দয়া করে আবার চেষ্টা করুন।\n"
                "If the problem persists, contact support."
            )
        except:
            pass
