from bot.handlers.base import BaseHandler
from bot.utils.translations import t
from telethon import Button

class DebtHandler(BaseHandler):
    async def show_debt_menu(self, event):
        user_id = event.sender_id
        buttons = [
            [Button.inline(t(user_id, 'give'), b"debt_give_0"), 
             Button.inline(t(user_id, 'take'), b"debt_take_0")],
            [Button.inline(t(user_id, 'i_repaid'), b"debt_i_repaid"), 
             Button.inline(t(user_id, 'he_repaid'), b"debt_he_repaid")],
            [Button.inline(t(user_id, 'debt_list'), b"debt_list")],
            [Button.inline(t(user_id, 'outstanding'), b"out_main")],
            [Button.inline(t(user_id, 'cancel'), b"cancel_state")]
        ]
        await event.respond(t(user_id, 'debt_manager'), buttons=buttons)
