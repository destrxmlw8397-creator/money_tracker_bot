import re
from telethon import Button
from bot.handlers.base import BaseHandler
from bot.utils.translations import t
from bot.utils.helpers import get_current_month, get_current_date, get_current_time, get_user_now
from bot.utils.temp_storage import store_temp_data
from bot.database.repositories import BalanceRepository, OutstandingRepository
from bot.services.transaction_service import (
    update_user_db, get_user_monthly_data, get_lifetime_wallet_balance,
    generate_pdf, show_wallets_for_debt, show_wallets_for_repayment,
    show_wallets_for_out_repayment
)

class MessageHandler(BaseHandler):
    user_states = {}
    
    async def handle_message(self, event):
        uid = event.sender_id
        text = event.text.strip()
        
        if text.startswith('/'):
            if text == '/reset':
                btns = [[Button.inline(t(uid, 'yes'), b"conf_reset_full"),
                        Button.inline(t(uid, 'no'), b"conf_no")]]
                await event.respond(t(uid, 'reset_confirm'), buttons=btns)
            return
        
        if uid in self.user_states:
            await self._handle_state(event, uid, text)
            return
        
        # Normal transaction entry
        data = get_user_monthly_data(uid, get_current_month(event))
        available_wallets = data.get('wallets', {"Cash": 0.0, "Bank": 0.0, "Bkash": 0.0})
        wallet = "Cash"
        for w in available_wallets.keys():
            if w.lower() in text.lower():
                wallet = w
                break
        
        match = re.search(r'([-+]?\d*\.?\d+)', text)
        if match:
            try:
                amount = float(match.group(1))
                pattern = '|'.join(map(re.escape, available_wallets.keys()))
                category = re.sub(pattern, '', text, flags=re.I)
                category = re.sub(r'[-+]?\d*\.?\d+', '', category).strip() or "General"
                update_user_db(uid, amount, category, wallet, event=event)
                emoji = t(uid, 'deposit') if amount > 0 else t(uid, 'expense')
                await event.reply(t(uid, 'entry_success', emoji, abs(amount), category, wallet))
            except Exception as e:
                print(f"Error: {e}")
    
    async def _handle_state(self, event, uid, text):
        state = self.user_states[uid]
        
        try:
            # Outstanding amount state
            if "ST_OUTAMT_" in state:
                parts = state.split("_")
                dtype = parts[2]
                name = parts[3]
                amt = float(text)
                user_time = get_user_now(event)
                OutstandingRepository.add_or_update(uid, name, dtype, amt)
                OutstandingHistoryRepository.add(
                    uid, name, amt,
                    get_current_date(event), get_current_time(event)
                )
                self.user_states.pop(uid)
                await event.respond(t(uid, 'out_entry_success', name, amt),
                                   buttons=[Button.inline(t(uid, 'back'), b"out_main")])
                return
            
            # Outstanding new person state
            elif "ST_OUTNEW_" in state:
                dtype = state.split("_")[2]
                parts = text.split()
                name, amt = parts[0], float(parts[1])
                user_time = get_user_now(event)
                OutstandingRepository.add_or_update(uid, name, dtype, amt)
                OutstandingHistoryRepository.add(
                    uid, name, amt,
                    get_current_date(event), get_current_time(event)
                )
                self.user_states.pop(uid)
                await event.respond(t(uid, 'out_new_success', name, amt),
                                   buttons=[Button.inline(t(uid, 'back'), b"out_main")])
                return
            
            # Outstanding repayment state
            elif "ST_OUTREPAY_" in state:
                d_id = int(state.split("_")[2])
                amt = float(text)
                debt = OutstandingRepository.get_by_id(d_id)
                if debt:
                    self.user_states.pop(uid)
                    await show_wallets_for_out_repayment(event, uid, debt['type'], debt['name'], amt, d_id, b"out_main")
                return
            
            # Date report state
            if state == "ST_REP_DATE":
                self.user_states.pop(uid)
                data = get_user_monthly_data(uid, get_current_month(event))
                income = sum(e['amount'] for e in data['history']
                            if e.get('date') == text and e['amount'] > 0
                            and (not e.get("is_debt_logic") or e.get("is_outstanding_repay")))
                expense = sum(abs(e['amount']) for e in data['history']
                             if e.get('date') == text and e['amount'] < 0
                             and (not e.get("is_debt_logic") or e.get("is_outstanding_repay")))
                await event.respond(
                    f"{t(uid, 'date_report', text)}\n━━━━━━━━━━━━━\n"
                    f"{t(uid, 'total_income')}: {income}\n"
                    f"{t(uid, 'total_expense')}: {expense}\n"
                    f"{t(uid, 'net')}: {income-expense}",
                    buttons=[Button.inline(t(uid, 'back'), b"rep_main")]
                )
                return
            
            # PDF month state
            elif state == "ST_PDF_MONTH":
                self.user_states.pop(uid)
                file = generate_pdf(uid, text)
                if file:
                    await self.client.send_file(event.chat_id, file, caption=t(uid, 'pdf_sent', text))
                    os.remove(file)
                else:
                    await event.respond(t(uid, 'pdf_no_data_month'))
                return
            
            # PDF date state
            elif state == "ST_PDF_DATE":
                self.user_states.pop(uid)
                file = generate_pdf(uid, get_current_month(event), history_filter=text)
                if file:
                    await self.client.send_file(event.chat_id, file, caption=t(uid, 'pdf_today_sent', text))
                    os.remove(file)
                else:
                    await event.respond(t(uid, 'pdf_no_data'))
                return
            
            # Set budget state
            elif state == "ST_SET_BUDGET":
                self.user_states.pop(uid)
                limit = float(text)
                data = get_user_monthly_data(uid, get_current_month(event))
                data['budget_limit'] = limit
                BalanceRepository.update_monthly_data(uid, get_current_month(event), data)
                await event.respond(t(uid, 'budget_set', limit))
                return
            
            # Add wallet state
            elif state == "ST_ADD_WALLET":
                self.user_states.pop(uid)
                wallet_name = text.strip()
                data = get_user_monthly_data(uid, get_current_month(event))
                wallets = data.get('wallets', {})
                if wallet_name in wallets:
                    await event.respond(t(uid, 'wallet_exists', wallet_name))
                else:
                    wallets[wallet_name] = 0.0
                    data['wallets'] = wallets
                    BalanceRepository.update_monthly_data(uid, get_current_month(event), data)
                    await event.respond(t(uid, 'wallet_added', wallet_name))
                return
            
            # New goal state
            elif state == "ST_NEW_GOAL":
                parts = text.split()
                name, target = parts[0], float(parts[1])
                GoalRepository.add_or_update(uid, name, target)
                self.user_states.pop(uid)
                await event.respond(t(uid, 'goal_set', name),
                                   buttons=[Button.inline(t(uid, 'back'), b"goal_main")])
                return
            
            # Save goal state
            elif "ST_SAVE_GOAL_" in state:
                gname = state.split("_")[3]
                amt = float(text)
                user_time = get_user_now(event)
                GoalRepository.add_savings(uid, gname, amt)
                GoalHistoryRepository.add(
                    uid, gname, amt,
                    get_current_date(event), get_current_time(event)
                )
                self.user_states.pop(uid)
                await event.respond(t(uid, 'goal_saved', amt, gname),
                                   buttons=[Button.inline(t(uid, 'back'), b"glist_0")])
                return
            
            # Transfer amount state
            elif "ST_TRNS_AMT_" in state:
                parts = state.split("_")
                w_from, w_to = parts[3], parts[4]
                amt = float(text)
                self.user_states.pop(uid)
                user_time = get_user_now(event)
                data = get_user_monthly_data(uid, user_time.strftime("%b-%Y"))
                wallets = data.get('wallets', {})
                
                lifetime_balance = get_lifetime_wallet_balance(uid, w_from)
                
                if lifetime_balance < amt:
                    await event.respond(t(uid, 'insufficient_balance', w_from, lifetime_balance, amt))
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
                    BalanceRepository.update_monthly_data(uid, user_time.strftime("%b-%Y"), data)
                    await event.respond(t(uid, 'transfer_success', amt, w_from, w_to),
                                       buttons=[Button.inline(t(uid, 'main_menu'), b"cancel_state")])
                return
            
            # Debt amount state
            elif "ST_AMT_" in state:
                parts = state.split("_")
                dtype = parts[2]
                name = parts[3]
                amount = float(text)
                self.user_states.pop(uid)
                await show_wallets_for_debt(event, uid, dtype, name, amount, f"debt_{dtype}_0")
                return
            
            # Debt new person state
            elif "ST_NEW_" in state:
                parts = state.split("_")
                dtype = parts[2]
                parts_text = text.split()
                name, amount = parts_text[0], float(parts_text[1])
                self.user_states.pop(uid)
                await show_wallets_for_debt(event, uid, dtype, name, amount, f"debt_{dtype}_0")
                return
            
            # Debt repayment state
            elif "ST_REPAY_AMT_" in state:
                parts = state.split("_")
                dtype = parts[3]
                debt_id = int(parts[4])
                name = parts[5]
                amount = float(text)
                self.user_states.pop(uid)
                
                if dtype == "take":
                    action_type = "i_repaid"
                else:
                    action_type = "he_repaid"
                
                return_callback = "debt_i_repaid" if dtype == "take" else "debt_he_repaid"
                await show_wallets_for_repayment(event, uid, action_type, name, amount, debt_id, return_callback)
                return
        
        except Exception as e:
            print(f"Error: {e}")
            await event.respond(t(uid, 'invalid_input'),
                               buttons=[Button.inline(t(uid, 'back'), b"debt_main_menu")])
            return
