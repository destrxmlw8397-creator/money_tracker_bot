"""
Message Handler Module
Handles regular messages (non-command) and user input states
"""

import re
import math
import logging
from telethon import Button
from bot.handlers.base import BaseHandler
from bot.utils.translations import t
from bot.utils.helpers import get_current_month, get_current_date, get_current_time, get_user_now
from bot.database.repositories import (
    BalanceRepository, DebtRepository, DebtHistoryRepository,
    OutstandingRepository, OutstandingHistoryRepository,
    GoalRepository, GoalHistoryRepository
)
from bot.services.transaction_service import (
    update_user_db, get_user_monthly_data, get_lifetime_wallet_balance,
    generate_pdf, show_wallets_for_debt, show_wallets_for_repayment,
    show_wallets_for_out_repayment
)

logger = logging.getLogger(__name__)


class MessageHandler(BaseHandler):
    """
    Handler for regular messages and user input states
    """
    
    # User states dictionary
    user_states = {}
    
    async def handle_message(self, event):
        """
        Handle regular messages (not commands)
        
        Args:
            event: Telegram event
        """
        uid = event.sender_id
        text = event.text.strip()
        
        # Handle /undo and /reset commands separately (kept here for simplicity)
        if text == '/undo':
            await self.undo_last_entry(event)
            return
        
        if text == '/reset':
            await self.reset_data(event)
            return
        
        # Skip any other command (starting with '/')
        # Because they are handled by specific command handlers
        if text.startswith('/'):
            return
        
        # Check if user is in a state (waiting for input)
        if uid in self.user_states:
            await self._handle_state(event, uid, text)
            return
        
        # Normal transaction entry
        await self._process_transaction_entry(event, uid, text)
    
    async def _process_transaction_entry(self, event, uid, text):
        """
        Process normal transaction entry (e.g., "500", "খাবার -300", "বিকাশ ২০০ বেতন")
        
        Args:
            event: Telegram event
            uid: User ID
            text: Input text
        """
        data = get_user_monthly_data(uid, get_current_month(event))
        available_wallets = data.get('wallets', {"Cash": 0.0, "Bank": 0.0, "Bkash": 0.0})
        
        # Detect wallet from text
        wallet = "Cash"
        for w in available_wallets.keys():
            if w.lower() in text.lower():
                wallet = w
                break
        
        # Extract amount
        match = re.search(r'([-+]?\d*\.?\d+)', text)
        if match:
            try:
                amount = float(match.group(1))
                
                # Extract category by removing wallet names and amount
                pattern = '|'.join(map(re.escape, available_wallets.keys()))
                category = re.sub(pattern, '', text, flags=re.I)
                category = re.sub(r'[-+]?\d*\.?\d+', '', category).strip()
                
                if not category:
                    category = "General"
                
                # Save transaction
                update_user_db(uid, amount, category, wallet, event=event)
                
                emoji = t(uid, 'deposit') if amount > 0 else t(uid, 'expense')
                await event.reply(t(uid, 'entry_success', emoji, abs(amount), category, wallet), parse_mode='html')
                
            except Exception as e:
                print(f"Error processing transaction: {e}")
    
    async def _handle_state(self, event, uid, text):
        """
        Handle user state inputs (waiting for amount, name, etc.)
        
        Args:
            event: Telegram event
            uid: User ID
            text: Input text
        """
        state = self.user_states[uid]
        
        try:
            # ==================== PDF STATES (MUST BE FIRST) ====================
            if state == "ST_PDF_MONTH":
                # User is entering month for PDF (e.g., Jan-2026)
                logger.info(f"Processing PDF MONTH state: {text}")
                self.user_states.pop(uid)
                from bot.handlers.pdf import PDFHandler
                ph = PDFHandler(self.client)
                await ph.generate_month_pdf(uid, event.chat_id, text)
                return
            
            elif state == "ST_PDF_DATE":
                # User is entering date for PDF (e.g., 01-01-2026)
                logger.info(f"Processing PDF DATE state: {text}")
                self.user_states.pop(uid)
                from bot.handlers.pdf import PDFHandler
                ph = PDFHandler(self.client)
                await ph.generate_date_pdf(uid, event.chat_id, text)
                return
            
            # ==================== OUTSTANDING STATES ====================
            if "ST_OUTAMT_" in state:
                # User is entering amount for outstanding (give/take)
                parts = state.split("_")
                dtype = parts[2]
                name = parts[3]
                amt = float(text)
                user_time = get_user_now(event)
                
                OutstandingRepository.add_or_update(uid, name, dtype, amt)
                OutstandingHistoryRepository.add(
                    uid, name, amt,
                    get_current_date(event),
                    get_current_time(event)
                )
                
                self.user_states.pop(uid)
                await event.respond(t(uid, 'out_entry_success', name, amt),
                                   buttons=[Button.inline(t(uid, 'back'), b"out_main")],
                                   parse_mode='html')
                return
            
            elif "ST_OUTNEW_" in state:
                # User is adding new person for outstanding
                dtype = state.split("_")[2]
                parts = text.split()
                name = parts[0]
                amt = float(parts[1])
                user_time = get_user_now(event)
                
                OutstandingRepository.add_or_update(uid, name, dtype, amt)
                OutstandingHistoryRepository.add(
                    uid, name, amt,
                    get_current_date(event),
                    get_current_time(event)
                )
                
                self.user_states.pop(uid)
                await event.respond(t(uid, 'out_new_success', name, amt),
                                   buttons=[Button.inline(t(uid, 'back'), b"out_main")],
                                   parse_mode='html')
                return
            
            elif "ST_OUTREPAY_" in state:
                # User is entering amount for outstanding repayment
                d_id = int(state.split("_")[2])
                amt = float(text)
                debt = OutstandingRepository.get_by_id(d_id)
                
                if debt:
                    self.user_states.pop(uid)
                    await show_wallets_for_out_repayment(
                        event, uid, debt['type'], debt['name'], amt, d_id, b"out_main"
                    )
                return
            
            # ==================== REPORT STATES ====================
            elif state == "ST_REP_DATE":
                # User is entering date for date-wise report
                self.user_states.pop(uid)
                data = get_user_monthly_data(uid, get_current_month(event))
                
                income = sum(e['amount'] for e in data['history']
                            if e.get('date') == text and e['amount'] > 0
                            and (not e.get("is_debt_logic") or e.get("is_outstanding_repay")))
                expense = sum(abs(e['amount']) for e in data['history']
                             if e.get('date') == text and e['amount'] < 0
                             and (not e.get("is_debt_logic") or e.get("is_outstanding_repay")))
                
                net = income - expense
                await event.respond(
                    f"{t(uid, 'date_report', text)}\n━━━━━━━━━━━━━\n"
                    f"{t(uid, 'total_income')}: {income:.2f}\n"
                    f"{t(uid, 'total_expense')}: {expense:.2f}\n"
                    f"{t(uid, 'net')}: {net:.2f}",
                    buttons=[Button.inline(t(uid, 'back'), b"rep_main")],
                    parse_mode='html'
                )
                return
            
            # ==================== WALLET STATES ====================
            elif state == "ST_SET_BUDGET":
                # User is entering budget amount
                self.user_states.pop(uid)
                limit = float(text)
                data = get_user_monthly_data(uid, get_current_month(event))
                data['budget_limit'] = limit
                BalanceRepository.update_monthly_data(uid, get_current_month(event), data)
                await event.respond(t(uid, 'budget_set', limit), parse_mode='html')
                return
            
            elif state == "ST_ADD_WALLET":
                # User is entering new wallet name
                self.user_states.pop(uid)
                wallet_name = text.strip()
                data = get_user_monthly_data(uid, get_current_month(event))
                wallets = data.get('wallets', {})
                
                if wallet_name in wallets:
                    await event.respond(t(uid, 'wallet_exists', wallet_name), parse_mode='html')
                else:
                    wallets[wallet_name] = 0.0
                    data['wallets'] = wallets
                    BalanceRepository.update_monthly_data(uid, get_current_month(event), data)
                    await event.respond(t(uid, 'wallet_added', wallet_name), parse_mode='html')
                return
            
            # ==================== GOAL STATES ====================
            elif state == "ST_NEW_GOAL":
                # User is entering new goal (name and target)
                parts = text.split()
                name = parts[0]
                target = float(parts[1])
                
                GoalRepository.add_or_update(uid, name, target)
                self.user_states.pop(uid)
                await event.respond(t(uid, 'goal_set', name),
                                   buttons=[Button.inline(t(uid, 'back'), b"goal_main")],
                                   parse_mode='html')
                return
            
            elif "ST_SAVE_GOAL_" in state:
                # User is entering amount to save to goal
                gname = state.split("_")[3]
                amt = float(text)
                user_time = get_user_now(event)
                
                GoalRepository.add_savings(uid, gname, amt)
                GoalHistoryRepository.add(
                    uid, gname, amt,
                    get_current_date(event),
                    get_current_time(event)
                )
                
                self.user_states.pop(uid)
                await event.respond(t(uid, 'goal_saved', amt, gname),
                                   buttons=[Button.inline(t(uid, 'back'), b"glist_0")],
                                   parse_mode='html')
                return
            
            # ==================== TRANSFER STATES ====================
            elif "ST_TRNS_AMT_" in state:
                # User is entering amount for transfer
                parts = state.split("_")
                w_from = parts[3]
                w_to = parts[4]
                amt = float(text)
                self.user_states.pop(uid)
                user_time = get_user_now(event)
                month_key = user_time.strftime("%b-%Y")
                data = get_user_monthly_data(uid, month_key)
                wallets = data.get('wallets', {})
                
                lifetime_balance = get_lifetime_wallet_balance(uid, w_from)
                
                if lifetime_balance < amt:
                    await event.respond(
                        t(uid, 'insufficient_balance', w_from, lifetime_balance, amt),
                        parse_mode='html'
                    )
                else:
                    wallets[w_from] -= amt
                    wallets[w_to] += amt
                    
                    entry = {
                        "amount": 0,
                        "category": f"Transfer: {w_from} to {w_to}",
                        "wallet": f"{w_from}/{w_to}",
                        "date": get_current_date(event),
                        "time": get_current_time(event),
                        "is_debt_logic": True
                    }
                    
                    data['history'].append(entry)
                    data['wallets'] = wallets
                    BalanceRepository.update_monthly_data(uid, month_key, data)
                    
                    await event.respond(
                        t(uid, 'transfer_success', amt, w_from, w_to),
                        buttons=[Button.inline(t(uid, 'main_menu'), b"cancel_state")],
                        parse_mode='html'
                    )
                return
            
            # ==================== DEBT STATES ====================
            elif "ST_AMT_" in state:
                # User is entering amount for debt (give/take)
                parts = state.split("_")
                dtype = parts[2]
                name = parts[3]
                amount = float(text)
                self.user_states.pop(uid)
                
                await show_wallets_for_debt(
                    event, uid, dtype, name, amount, f"debt_{dtype}_0"
                )
                return
            
            elif "ST_NEW_" in state:
                # User is entering new person for debt
                parts = state.split("_")
                dtype = parts[2]
                parts_text = text.split()
                name = parts_text[0]
                amount = float(parts_text[1])
                self.user_states.pop(uid)
                
                await show_wallets_for_debt(
                    event, uid, dtype, name, amount, f"debt_{dtype}_0"
                )
                return
            
            elif "ST_REPAY_AMT_" in state:
                # User is entering amount for debt repayment
                parts = state.split("_")
                dtype = parts[3]
                debt_id = int(parts[4])
                name = parts[5]
                amount = float(text)
                self.user_states.pop(uid)
                
                action_type = "i_repaid" if dtype == "take" else "he_repaid"
                return_callback = "debt_i_repaid" if dtype == "take" else "debt_he_repaid"
                
                await show_wallets_for_repayment(
                    event, uid, action_type, name, amount, debt_id, return_callback
                )
                return
            
        except Exception as e:
            print(f"Error in state handler: {e}")
            self.user_states.pop(uid, None)
            await event.respond(
                t(uid, 'invalid_input'),
                buttons=[Button.inline(t(uid, 'back'), b"debt_main_menu")],
                parse_mode='html'
            )
    
    async def undo_last_entry(self, event):
        """
        Handle /undo command - delete last transaction entry
        
        Args:
            event: Telegram event
        """
        uid = event.sender_id
        month_key = get_current_month(event)
        data = get_user_monthly_data(uid, month_key)
        
        if data and data.get('history'):
            last = data['history'].pop()
            wallet = last.get('wallet', 'Cash')
            new_wallets = data['wallets']
            new_wallets[wallet] = new_wallets.get(wallet, 0.0) - last['amount']
            
            is_debt = last.get("is_debt_logic", False)
            is_out_rep = last.get("is_outstanding_repay", False)
            
            if not is_debt or is_out_rep:
                if last['amount'] > 0:
                    data['total_income'] -= last['amount']
                else:
                    data['total_expense'] -= abs(last['amount'])
            
            data['wallets'] = new_wallets
            BalanceRepository.update_monthly_data(uid, month_key, data)
            
            await event.respond(t(uid, 'undo_success', last.get('category', 'Unknown')), parse_mode='html')
        else:
            await event.respond(t(uid, 'no_history'), parse_mode='html')
    
    async def reset_data(self, event):
        """
        Handle /reset command - show reset confirmation options
        
        Args:
            event: Telegram event
        """
        uid = event.sender_id
        month_key = get_current_month(event)
        
        buttons = [
            [Button.inline(t(uid, 'reset_month_confirm', month_key), b"reset_month")],
            [Button.inline(t(uid, 'reset_all_success'), b"reset_all")],
            [Button.inline(t(uid, 'cancel'), b"cancel_state")]
        ]
        
        await event.respond(t(uid, 'reset_confirm'), buttons=buttons, parse_mode='html')
    
    async def reset_full_database(self, event):
        """
        Reset all user data (called from callback)
        
        Args:
            event: Telegram event
        """
        uid = event.sender_id
        BalanceRepository.delete_user_data(uid)
        DebtRepository.delete_user_data(uid)
        DebtHistoryRepository.delete_user_data(uid)
        GoalRepository.delete_user_data(uid)
        GoalHistoryRepository.delete_user_data(uid)
        OutstandingRepository.delete_user_data(uid)
        OutstandingHistoryRepository.delete_user_data(uid)
        await event.edit(t(uid, 'reset_all_success'), parse_mode='html')
