import math
from bot.handlers.base import BaseHandler
from bot.utils.translations import t
from bot.database.repositories import BalanceRepository, DebtRepository
from telethon import Button

class BalanceHandler(BaseHandler):
    async def show_balance(self, event):
        await self.send_balance_page(event.sender_id, event.chat_id, -1)
    
    async def send_balance_page(self, user_id, chat_id, page_index, message_id=None):
        all_months = BalanceRepository.get_all_months(user_id)
        all_months = all_months[::-1]
        total_months = len(all_months)
        
        total_income_life = sum(m.get('total_income', 0) for m in all_months)
        total_expense_life = sum(m.get('total_expense', 0) for m in all_months)
        
        final_wallets = {}
        for month in all_months:
            for w, v in month.get('wallets', {}).items():
                final_wallets[w] = final_wallets.get(w, 0) + v
        
        debts = DebtRepository.get_all(user_id)
        total_receivable = sum(d['amount'] for d in debts if d['type'] == 'give')
        total_payable = sum(d['amount'] for d in debts if d['type'] == 'take')
        net_life = sum(final_wallets.values())
        
        buttons = []
        
        if page_index == -1:
            wallet_info = "\n".join([t(user_id, 'wallet_balance', w, v) for w, v in final_wallets.items()]) if final_wallets else t(user_id, 'no_wallet')
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
                f"{t(user_id, 'net_balance', net_life)}\n"
            )
            if total_months > 0:
                buttons.append([Button.inline(t(user_id, 'next_month'), "balp_0")])
        else:
            if all_months:
                target = all_months[page_index]
                m_key = target.get('month', 'Unknown')
                t_inc = target.get('total_income', 0)
                t_exp = target.get('total_expense', 0)
                wallets = target.get('wallets', {})
                budget = target.get('budget_limit', 0)
                net_month = sum(wallets.values())
                
                m_receivable = m_payable = 0.0
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
                
                wallet_info = "\n".join([t(user_id, 'wallet_balance', w, v) for w, v in wallets.items()])
                usage = (t_exp / budget * 100) if budget > 0 else 0
                
                msg = (
                    f"{t(user_id, 'monthly_report', m_key)}\n"
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
                    f"{t(user_id, 'budget_usage', usage, t_exp, budget)}"
                )
                
                nav = []
                if page_index == 0:
                    nav.append(Button.inline(t(user_id, 'previous_life'), "balp_-1"))
                else:
                    nav.append(Button.inline(t(user_id, 'previous_month'), f"balp_{page_index - 1}"))
                if page_index < total_months - 1:
                    nav.append(Button.inline(t(user_id, 'next_month'), f"balp_{page_index + 1}"))
                buttons.append(nav)
            else:
                msg = t(user_id, 'no_data')
        
        if message_id:
            await self.client.edit_message(chat_id, message_id, msg, buttons=buttons or None)
        else:
            await self.client.send_message(chat_id, msg, buttons=buttons or None)
