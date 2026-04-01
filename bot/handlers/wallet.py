"""
Wallet Handler Module
Handles wallet management commands: /setbudget, /addwallet, /delwallet
"""

import math
from telethon import Button
from bot.handlers.base import BaseHandler
from bot.utils.translations import t
from bot.utils.helpers import get_current_month
from bot.database.repositories import BalanceRepository


class WalletHandler(BaseHandler):
    """
    Handler for wallet management commands
    """
    
    # User states for wallet operations
    user_states = {}
    
    # ==================== SET BUDGET ====================
    
    async def set_budget(self, event):
        """
        Handle /setbudget command - prompt for budget amount
        
        Args:
            event: Telegram event
        """
        user_id = event.sender_id
        self.user_states[user_id] = "ST_SET_BUDGET"
        
        await event.respond(
            t(user_id, 'enter_budget'),
            buttons=[Button.inline(t(user_id, 'cancel'), b"cancel_state")]
        )
    
    async def process_budget_input(self, user_id, amount):
        """
        Process budget input and save to database
        
        Args:
            user_id: User ID
            amount: Budget amount
            
        Returns:
            bool: True if successful
        """
        try:
            month_key = get_current_month()
            data = BalanceRepository.get_monthly_data(user_id, month_key)
            data['budget_limit'] = float(amount)
            BalanceRepository.update_monthly_data(user_id, month_key, data)
            return True
        except Exception as e:
            print(f"Error saving budget: {e}")
            return False
    
    # ==================== ADD WALLET ====================
    
    async def add_wallet(self, event):
        """
        Handle /addwallet command - prompt for wallet name
        
        Args:
            event: Telegram event
        """
        user_id = event.sender_id
        self.user_states[user_id] = "ST_ADD_WALLET"
        
        await event.respond(
            t(user_id, 'enter_wallet_name'),
            buttons=[Button.inline(t(user_id, 'cancel'), b"cancel_state")]
        )
    
    async def process_add_wallet_input(self, user_id, wallet_name):
        """
        Process add wallet input and save to database
        
        Args:
            user_id: User ID
            wallet_name: Name of new wallet
            
        Returns:
            tuple: (success, message)
        """
        try:
            month_key = get_current_month()
            data = BalanceRepository.get_monthly_data(user_id, month_key)
            wallets = data.get('wallets', {})
            
            # Check if wallet already exists
            if wallet_name in wallets:
                return False, t(user_id, 'wallet_exists', wallet_name)
            
            # Add new wallet with zero balance
            wallets[wallet_name] = 0.0
            data['wallets'] = wallets
            BalanceRepository.update_monthly_data(user_id, month_key, data)
            
            return True, t(user_id, 'wallet_added', wallet_name)
            
        except Exception as e:
            print(f"Error adding wallet: {e}")
            return False, f"❌ ত্রুটি: {e}"
    
    # ==================== DELETE WALLET ====================
    
    async def delete_wallet(self, event):
        """
        Handle /delwallet command - show wallet list to delete
        
        Args:
            event: Telegram event
        """
        await self.show_del_wallet_list(event, 0)
    
    async def show_del_wallet_list(self, event, page):
        """
        Show list of wallets for deletion
        
        Args:
            event: Telegram event
            page: Page number for pagination
        """
        user_id = event.sender_id
        month_key = get_current_month(event)
        data = BalanceRepository.get_monthly_data(user_id, month_key)
        wallets = data.get('wallets', {})
        all_wallets = list(wallets.keys())
        
        if not all_wallets:
            await event.respond(t(user_id, 'no_wallet'))
            return
        
        page_size = 10
        total_pages = max(1, (len(all_wallets) + page_size - 1) // page_size)
        start = page * page_size
        wallets_slice = all_wallets[start:start + page_size]
        
        msg = f"{t(user_id, 'select_wallet_delete')}\n"
        msg += f"{t(user_id, 'page')}: {page + 1} / {total_pages}"
        
        buttons = []
        for w in wallets_slice:
            buttons.append([Button.inline(f"🗑️ {w}", f"dw_sel_{w}")])
        
        # Navigation buttons
        nav_buttons = []
        if page > 0:
            nav_buttons.append(Button.inline(t(user_id, 'previous'), f"dw_list_{page-1}"))
        if page + 1 < total_pages:
            nav_buttons.append(Button.inline(t(user_id, 'next'), f"dw_list_{page+1}"))
        if nav_buttons:
            buttons.append(nav_buttons)
        
        # Cancel button
        buttons.append([Button.inline(t(user_id, 'cancel'), b"cancel_state")])
        
        try:
            await event.edit(msg, buttons=buttons)
        except Exception:
            await event.respond(msg, buttons=buttons)
    
    async def confirm_delete_wallet(self, event, wallet_name):
        """
        Show confirmation dialog for wallet deletion
        
        Args:
            event: Telegram event
            wallet_name: Name of wallet to delete
        """
        user_id = event.sender_id
        
        buttons = [
            [
                Button.inline(t(user_id, 'confirm'), f"dw_conf_{wallet_name}"),
                Button.inline(t(user_id, 'no'), b"dw_list_0")
            ]
        ]
        
        await event.edit(t(user_id, 'delete_wallet_confirm', wallet_name), buttons=buttons)
    
    async def execute_delete_wallet(self, event, wallet_name):
        """
        Execute wallet deletion
        
        Args:
            event: Telegram event
            wallet_name: Name of wallet to delete
        """
        user_id = event.sender_id
        month_key = get_current_month(event)
        data = BalanceRepository.get_monthly_data(user_id, month_key)
        wallets = data.get('wallets', {})
        
        if wallet_name in wallets:
            # Remove wallet
            del wallets[wallet_name]
            data['wallets'] = wallets
            BalanceRepository.update_monthly_data(user_id, month_key, data)
            
            await event.edit(
                t(user_id, 'wallet_deleted', wallet_name),
                buttons=[Button.inline(t(user_id, 'back'), b"dw_list_0")]
            )
        else:
            await event.answer(t(user_id, 'no_data'), alert=True)
    
    # ==================== HELPER METHODS ====================
    
    def get_user_state(self, user_id):
        """
        Get user state
        
        Args:
            user_id: User ID
            
        Returns:
            str: User state or None
        """
        return self.user_states.get(user_id)
    
    def clear_user_state(self, user_id):
        """
        Clear user state
        
        Args:
            user_id: User ID
        """
        self.user_states.pop(user_id, None)
