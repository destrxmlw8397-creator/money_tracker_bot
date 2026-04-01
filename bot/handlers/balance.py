"""
Balance Handler Module
Handles /balance command with pagination for monthly and lifetime reports
"""

import math
from telethon import Button
from bot.handlers.base import BaseHandler
from bot.utils.translations import t
from bot.database.repositories import BalanceRepository, DebtRepository


class BalanceHandler(BaseHandler):
    """
    Handler for /balance command
    Displays lifetime and monthly reports with wallet balances
    """
    
    async def show_balance(self, event):
        """
        Handle /balance command - show lifetime report
        
        Args:
            event: Telegram event
        """
        await self.send_balance_page(event.sender_id, event.chat_id, -1)
    
    async def send_balance_page(self, user_id, chat_id, page_index, message_id=None):
        """
        Send balance page with pagination
        
        Args:
            user_id: User ID
            chat_id: Chat ID to send to
            page_index: -1 for lifetime, 0+ for monthly pages
            message_id: Optional message ID to edit instead of send new
        """
        # Get all months data
        all_months = BalanceRepository.get_all_months(user_id)
        all_months = all_months[::-1]  # Latest first
        total_months = len(all_months)
        
        # Calculate lifetime totals
        total_income_life = sum(m.get('total_income', 0) for m in all_months)
        total_expense_life = sum(m.get('total_expense', 0) for m in all_months)
        
        # Calculate lifetime wallet balances
        final_wallets = {}
        for month in all_months:
            for w_name, w_balance in month.get('wallets', {}).items():
                final_wallets[w_name] = final_wallets.get(w_name, 0) + w_balance
        
        # Get debt totals
        all_debts = DebtRepository.get_all(user_id)
        total_receivable = sum(d['amount'] for d in all_debts if d['type'] == 'give')
        total_payable = sum(d['amount'] for d in all_debts if d['type'] == 'take')
        net_life_wallet = sum(final_wallets.values())
        
        buttons = []
        
        # Lifetime report (page_index = -1)
        if page_index == -1:
            wallet_info = "\n".join([
                t(user_id, 'wallet_balance', w, v)
                for w, v in final_wallets.items()
            ]) if final_wallets else t(user_id, 'no_wallet')
            
            msg = (
                f"{t(user_id, 'lifetime_report')}\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"{t(user_id, 'total_income')}: {total_income_life:.2f}\n"
                f"{t(user_id, 'total_expense')}: {total_expense_life:.2f}\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"{t(user_id, 'total_receivable')}: {total_receivable:.2f}\n"
                f"{t(user_id, 'total_payable')}: {total_payable:.2f}\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"{t(user_id, 'current_wallet')}\n{wallet_info}\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"{t(user_id, 'net_balance', net_life_wallet)}\n"
            )
            
            if total_months > 0:
                buttons.append([Button.inline(t(user_id, 'next_month'), "balp_0")])
        
        # Monthly report
        else:
            if not all_months or page_index >= len(all_months):
                msg = t(user_id, 'no_data')
            else:
                target = all_months[page_index]
                month_key = target.get('month', 'Unknown')
                t_inc = target.get('total_income', 0)
                t_exp = target.get('total_expense', 0)
                wallets = target.get('wallets', {})
                budget = target.get('budget_limit', 0)
                net_month = sum(wallets.values())
                
                # Calculate monthly debt from history
                m_receivable = 0.0
                m_payable = 0.0
                
                for entry in target.get('history', []):
                    if entry.get('is_debt_logic'):
                        cat = entry.get('category', '')
                        amt = entry.get('amount', 0)
                        if "Loan to" in cat:
                            m_receivable += abs(amt)
                        elif "Loan from" in cat:
                            m_payable += abs(amt)
                        elif "Repayment from" in cat:
                            m_receivable -= abs(amt)
                        elif "Repayment to" in cat:
                            m_payable -= abs(amt)
                
                wallet_info = "\n".join([
                    t(user_id, 'wallet_balance', w, v)
                    for w, v in wallets.items()
                ])
                usage_percent = (t_exp / budget * 100) if budget > 0 else 0
                
                msg = (
                    f"{t(user_id, 'monthly_report', month_key)}\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"{t(user_id, 'total_income')}:  {t_inc:.2f}\n"
                    f"{t(user_id, 'total_expense')}:  {t_exp:.2f}\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"{t(user_id, 'monthly_receivable')}: {m_receivable:.2f}\n"
                    f"{t(user_id, 'monthly_payable')}: {m_payable:.2f}\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"{t(user_id, 'current_wallet')}\n{wallet_info}\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"{t(user_id, 'remaining', net_month)}\n\n"
                    f"{t(user_id, 'budget_usage', usage_percent, t_exp, budget)}"
                )
                
                # Navigation buttons
                nav_row = []
                if page_index == 0:
                    nav_row.append(Button.inline(t(user_id, 'previous_life'), "balp_-1"))
                else:
                    nav_row.append(Button.inline(t(user_id, 'previous_month'), f"balp_{page_index - 1}"))
                if page_index < total_months - 1:
                    nav_row.append(Button.inline(t(user_id, 'next_month'), f"balp_{page_index + 1}"))
                buttons.append(nav_row)
        
        # Send or edit message
        if message_id:
            await self.client.edit_message(chat_id, message_id, msg, buttons=buttons if buttons else None)
        else:
            await self.client.send_message(chat_id, msg, buttons=buttons if buttons else None)
