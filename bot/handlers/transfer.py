"""
Transfer Handler Module
Handles /trns_money command for transferring money between wallets
"""

import math
from telethon import Button
from bot.handlers.base import BaseHandler
from bot.utils.translations import t
from bot.utils.helpers import get_current_month
from bot.services.transaction_service import get_user_monthly_data, get_lifetime_wallet_balance


class TransferHandler(BaseHandler):
    """
    Handler for /trns_money command
    Transfers money from one wallet to another
    """
    
    async def start_transfer(self, event):
        """
        Handle /trns_money command - start transfer process
        
        Args:
            event: Telegram event
        """
        await self.show_transfer_wallets(event, 0, "from")
    
    async def show_transfer_wallets(self, event, page, mode, wallet_from=None):
        """
        Show wallet selection for transfer
        
        Args:
            event: Telegram event
            page: Page number for pagination
            mode: 'from' for source wallet, 'to' for destination wallet
            wallet_from: Source wallet name (when mode='to')
        """
        user_id = event.sender_id
        data = get_user_monthly_data(user_id, get_current_month(event))
        wallets = data.get('wallets', {})
        
        if mode == "from":
            all_wallets = list(wallets.keys())
            msg_header = t(user_id, 'transfer_from')
        else:
            lifetime_balance = get_lifetime_wallet_balance(user_id, wallet_from)
            msg_header = (
                f"{t(user_id, 'transfer_to', wallet_from)}\n"
                f"{t(user_id, 'lifetime_balance_info', lifetime_balance)}"
            )
            all_wallets = [w for w in wallets.keys() if w != wallet_from]
        
        # Check if there are wallets
        if not all_wallets:
            await event.edit(t(user_id, 'no_wallet'))
            return
        
        page_size = 10
        total_pages = max(1, (len(all_wallets) + page_size - 1) // page_size)
        start = page * page_size
        wallets_slice = all_wallets[start:start + page_size]
        
        msg = f"{msg_header}\n━━━━━━━━━━━━━━━━━━\n"
        msg += f"{t(user_id, 'page')}: {page + 1} / {total_pages}"
        
        btns = []
        for w in wallets_slice:
            callback = f"tsel_f_{w}" if mode == "from" else f"tsel_t_{wallet_from}_{w}"
            btns.append([Button.inline(f"{w} ({wallets[w]:.2f})", callback)])
        
        # Navigation buttons
        nav_btns = []
        if page > 0:
            p_cb = f"t_from_{page-1}" if mode == "from" else f"t_to_{page-1}_{wallet_from}"
            nav_btns.append(Button.inline(t(user_id, 'previous'), p_cb))
        if page + 1 < total_pages:
            n_cb = f"t_from_{page+1}" if mode == "from" else f"t_to_{page+1}_{wallet_from}"
            nav_btns.append(Button.inline(t(user_id, 'next'), n_cb))
        
        if nav_btns:
            btns.append(nav_btns)
        
        # Back button for destination selection
        if mode == "to":
            btns.append([Button.inline(t(user_id, 'back_to_from'), "t_from_0")])
        
        btns.append([Button.inline(t(user_id, 'cancel'), b"cancel_state")])
        
        try:
            await event.edit(msg, buttons=btns)
        except Exception:
            await event.respond(msg, buttons=btns)
    
    async def prompt_transfer_amount(self, event, wallet_from, wallet_to):
        """
        Show prompt for transfer amount
        
        Args:
            event: Telegram event
            wallet_from: Source wallet name
            wallet_to: Destination wallet name
        """
        user_id = event.sender_id
        
        buttons = [
            [Button.inline(t(user_id, 'back'), f"tsel_f_{wallet_from}")],
            [Button.inline(t(user_id, 'cancel'), b"cancel_state")]
        ]
        
        await event.edit(
            t(user_id, 'enter_transfer_amount', wallet_from, wallet_to),
            buttons=buttons
        )
    
    async def execute_transfer(self, user_id, wallet_from, wallet_to, amount):
        """
        Execute the transfer
        
        Args:
            user_id: User ID
            wallet_from: Source wallet name
            wallet_to: Destination wallet name
            amount: Amount to transfer
            
        Returns:
            tuple: (success, message)
        """
        from bot.services.transaction_service import get_user_monthly_data, get_lifetime_wallet_balance
        from bot.database.repositories import BalanceRepository
        from bot.utils.helpers import get_current_month, get_current_date, get_current_time
        
        # Check if source wallet has enough balance
        lifetime_balance = get_lifetime_wallet_balance(user_id, wallet_from)
        
        if lifetime_balance < amount:
            return False, f"❌ পর্যাপ্ত ব্যালেন্স নেই! **{wallet_from}** এ আছে: **{lifetime_balance:.2f}** টাকা, লাগবে: **{amount:.2f}** টাকা"
        
        # Get current month data
        month_key = get_current_month()
        data = get_user_monthly_data(user_id, month_key)
        wallets = data.get('wallets', {})
        
        # Update wallet balances
        wallets[wallet_from] = wallets.get(wallet_from, 0) - amount
        wallets[wallet_to] = wallets.get(wallet_to, 0) + amount
        
        # Add transfer entry to history
        entry = {
            "amount": 0,
            "category": f"Transfer: {wallet_from} to {wallet_to}",
            "wallet": f"{wallet_from}/{wallet_to}",
            "date": get_current_date(),
            "time": get_current_time(),
            "is_debt_logic": True
        }
        
        data['history'].append(entry)
        data['wallets'] = wallets
        
        # Save to database
        BalanceRepository.update_monthly_data(user_id, month_key, data)
        
        return True, f"✅ সফলভাবে **{amount:.2f}** টাকা **{wallet_from}** থেকে **{wallet_to}** এ স্থানান্তরিত হয়েছে।"
