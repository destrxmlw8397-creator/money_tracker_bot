from bot.handlers.base import BaseHandler
from bot.utils.translations import t
from bot.utils.helpers import get_current_month
from bot.database.repositories import BalanceRepository
from telethon import Button

class WalletHandler(BaseHandler):
    async def set_budget(self, event):
        user_id = event.sender_id
        from bot.handlers.message import MessageHandler
        MessageHandler.user_states[user_id] = "ST_SET_BUDGET"
        await event.respond(t(user_id, 'enter_budget'), buttons=[Button.inline(t(user_id, 'cancel'), b"cancel_state")])
    
    async def add_wallet(self, event):
        user_id = event.sender_id
        from bot.handlers.message import MessageHandler
        MessageHandler.user_states[user_id] = "ST_ADD_WALLET"
        await event.respond(t(user_id, 'enter_wallet_name'), buttons=[Button.inline(t(user_id, 'cancel'), b"cancel_state")])
    
    async def delete_wallet(self, event):
        await self.show_del_wallet_list(event, 0)
    
    async def show_del_wallet_list(self, event, page):
        user_id = event.sender_id
        data = BalanceRepository.get_monthly_data(user_id, get_current_month(event))
        wallets = data.get('wallets', {})
        all_wallets = list(wallets.keys())
        page_size = 10
        total_pages = math.ceil(len(all_wallets) / page_size)
        start = page * page_size
        wallets_slice = all_wallets[start:start + page_size]
        msg = f"{t(user_id, 'select_wallet_delete')}\n{t(user_id, 'page')}: {page + 1} / {max(1, total_pages)}"
        btns = [[Button.inline(f"🗑️ {w}", f"dw_sel_{w}")] for w in wallets_slice]
        nav = []
        if page > 0:
            nav.append(Button.inline(t(user_id, 'previous'), f"dw_list_{page-1}"))
        if (page + 1) < total_pages:
            nav.append(Button.inline(t(user_id, 'next'), f"dw_list_{page+1}"))
        if nav:
            btns.append(nav)
        btns.append([Button.inline(t(user_id, 'cancel'), b"cancel_state")])
        try:
            await event.edit(msg, buttons=btns)
        except:
            await event.respond(msg, buttons=btns)
