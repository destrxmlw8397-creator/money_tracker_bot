from bot.handlers.base import BaseHandler
from bot.utils.translations import t
from telethon import Button

class GoalHandler(BaseHandler):
    async def show_goal_menu(self, event):
        user_id = event.sender_id
        btns = [
            [Button.inline(t(user_id, 'goal_list'), b"glist_0")],
            [Button.inline(t(user_id, 'goal_details'), b"gdet_0")],
            [Button.inline(t(user_id, 'cancel'), b"cancel_state")]
        ]
        await event.respond(t(user_id, 'goal_manager'), buttons=btns)
