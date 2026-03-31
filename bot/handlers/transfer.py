import math
from bot.handlers.base import BaseHandler
from bot.utils.translations import t
from bot.utils.helpers import get_current_month
from bot.services.transaction_service import get_user_monthly_data, get_lifetime_wallet_balance
from telethon import Button

class TransferHandler(BaseHandler):
    async def start_transfer(self, event):
        await self.show_transfer_wallets(event, 0, "from")
    
    async def show_transfer_wallets(self, event, page, mode, wallet_from=None):
        user_id = event.sender_id
        data = get_user_monthly_data(user_id, get_current_month(event))
        wallets = data.get('wallets', {})
        
        if mode == "from":
            all_wallets = list(wallets.keys())
            msg_header = t(user_id, 'transfer_from')
        else:
            lifetime_balance = get_lifetime_wallet_balance(user_id, wallet_from)
            msg_header = f"{t(user_id, 'transfer_to', wallet_from)}\n{t(user_id, 'lifetime_balance_info', lifetime_balance)}"
            all_wallets = [w for w in wallets.keys() if w != wallet_from]
        
        page_size = 10
        total_pages = math.ceil(len(all_wallets) / page_size)
        start = page * page_size
        wallets_slice = all_wallets[start:start + page_size]
        
        msg = f"{msg_header}\n━━━━━━━━━━━━━━━━━━\n{t(user_id, 'page')}: {page + 1} / {max(1, total_pages)}"
        btns = []
        for w in wallets_slice:
            callback = f"tsel_f_{w}" if mode == "from" else f"tsel_t_{wallet_from}_{w}"
            btns.append([Button.inline(f"{w} ({wallets[w]:.2f})", callback)])
        
        nav = []
        if page > 0:
            p_cb = f"t_from_{page-1}" if mode == "from" else f"t_to_{page-1}_{wallet_from}"
            nav.append(Button.inline(t(user_id, 'previous'), p_cb))
        if (page + 1) < total_pages:
            n_cb = f"t_from_{page+1}" if mode == "from" else f"t_to_{page+1}_{wallet_from}"
            nav.append(Button.inline(t(user_id, 'next'), n_cb))
        if nav:
            btns.append(nav)
        if mode == "to":
            btns.append([Button.inline(t(user_id, 'back_to_from'), "t_from_0")])
        btns.append([Button.inline(t(user_id, 'cancel'), b"cancel_state")])
        
        try:
            await event.edit(msg, buttons=btns)
        except:
            await event.respond(msg, buttons=btns)
