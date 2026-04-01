"""
Callback Handler Module
Handles all inline button callbacks for the bot
"""

import math
import os
from telethon import Button
from bot.handlers.base import BaseHandler
from bot.utils.translations import t, set_user_lang
from bot.utils.helpers import get_current_month, get_current_date, get_current_time, get_user_now
from bot.utils.temp_storage import get_temp_data
from bot.database.repositories import (
    BalanceRepository, DebtRepository, DebtHistoryRepository,
    OutstandingRepository, OutstandingHistoryRepository,
    GoalRepository, GoalHistoryRepository
)
from bot.services.transaction_service import (
    process_debt_entry_with_balance, process_debt_repayment,
    update_user_db, get_user_monthly_data,
    get_lifetime_wallet_balance, generate_pdf
)


class CallbackHandler(BaseHandler):
    """
    Handler for all callback queries from inline buttons
    """

    async def handle(self, event):
        """
        Main callback handler - routes to appropriate sub-handler

        Args:
            event: Telegram callback query event
        """
        user_id = event.sender_id
        data = event.data.decode('utf-8')
        month_key = get_current_month(event)

        # ==================== LANGUAGE HANDLERS ====================
        if data == "lang_bn":
            set_user_lang(user_id, "bn")
            await event.edit(t(user_id, 'language_set'))
            return
        elif data == "lang_en":
            set_user_lang(user_id, "en")
            await event.edit(t(user_id, 'language_set'))
            return

        # ==================== TEMP DATA HANDLERS ====================
        if data.startswith("tmp_"):
            temp_id = int(data.split("_")[1])
            cb_data = get_temp_data(temp_id)

            if cb_data:
                if cb_data['type'] == 'debt_wallet':
                    action_type = cb_data['action']
                    name = cb_data['name']
                    amount = cb_data['amount']
                    wallet_name = cb_data['wallet']

                    if action_type == "give":
                        process_debt_entry_with_balance(user_id, name, amount, "give", wallet_name, event)
                        await event.respond(t(user_id, 'updated', name, amount),
                                           buttons=[Button.inline(t(user_id, 'back'), b"debt_main_menu")])
                    elif action_type == "take":
                        process_debt_entry_with_balance(user_id, name, amount, "take", wallet_name, event)
                        await event.respond(t(user_id, 'updated', name, amount),
                                           buttons=[Button.inline(t(user_id, 'back'), b"debt_main_menu")])
                    await event.delete()
                    return

                elif cb_data['type'] == 'repay_wallet':
                    action_type = cb_data['action']
                    name = cb_data['name']
                    amount = cb_data['amount']
                    debt_id = cb_data['debt_id']
                    wallet_name = cb_data['wallet']

                    new_bal = process_debt_repayment(user_id, debt_id, amount, wallet_name, event)
                    await event.respond(t(user_id, 'repay_success', new_bal),
                                       buttons=[Button.inline(t(user_id, 'back'), b"debt_main_menu")])
                    await event.delete()
                    return

                elif cb_data['type'] == 'out_repay_wallet':
                    debt_type = cb_data['debt_type']
                    name = cb_data['name']
                    amount = cb_data['amount']
                    debt_id = cb_data['debt_id']
                    wallet_name = cb_data['wallet']

                    debt = OutstandingRepository.get_by_id(debt_id)
                    if debt:
                        new_bal = max(0, debt['amount'] - amount)
                        OutstandingRepository.update_amount(debt_id, new_bal)
                        OutstandingHistoryRepository.add(
                            user_id, name, -amount,
                            get_current_date(event), get_current_time(event)
                        )

                        if debt_type == "give":
                            update_user_db(user_id, amount, f"Out-Repay from {name}", wallet_name, event)
                        else:
                            update_user_db(user_id, -amount, f"Out-Repay to {name}", wallet_name, event)

                        await event.respond(t(user_id, 'out_repay_success', new_bal),
                                           buttons=[Button.inline(t(user_id, 'back'), b"out_main")])
                    await event.delete()
                    return

        # ==================== BALANCE PAGINATION ====================
        if data.startswith("balp_"):
            from bot.handlers.balance import BalanceHandler
            idx = int(data.split("_")[1])
            bh = BalanceHandler(self.client)
            await bh.send_balance_page(user_id, event.chat_id, idx, event.message_id)
            return

        # ==================== PDF HANDLERS ====================
        if data == "pdf_current":
            file = generate_pdf(user_id, month_key, title_suffix=f"Full {month_key}")
            if file:
                await self.client.send_file(event.chat_id, file, caption=t(user_id, 'pdf_sent', month_key))
                os.remove(file)
            else:
                await event.answer(t(user_id, 'no_data'), alert=True)
            return

        elif data == "pdf_month_wise":
            from bot.handlers.pdf import PDFHandler
            PDFHandler.user_states[user_id] = "ST_PDF_MONTH"
            await event.edit(t(user_id, 'pdf_month_prompt'),
                           buttons=[Button.inline(t(user_id, 'back'), b"pdf_main")])
            return

        elif data == "pdf_main":
            from bot.handlers.pdf import PDFHandler
            PDFHandler.user_states.pop(user_id, None)
            buttons = [
                [Button.inline(t(user_id, 'pdf_current'), b"pdf_current")],
                [Button.inline(t(user_id, 'pdf_month_wise'), b"pdf_month_wise")],
                [Button.inline(t(user_id, 'pdf_today'), b"pdf_today")],
                [Button.inline(t(user_id, 'pdf_date_wise'), b"pdf_date_wise")],
                [Button.inline(t(user_id, 'cancel'), b"cancel_state")]
            ]
            await event.edit(t(user_id, 'pdf_options'), buttons=buttons)
            return

        elif data == "pdf_today":
            today = get_current_date(event)
            file = generate_pdf(user_id, month_key, history_filter=today, title_suffix=f"Today ({today})")
            if file:
                await self.client.send_file(event.chat_id, file, caption=t(user_id, 'pdf_today_sent', today))
                os.remove(file)
            else:
                await event.answer(t(user_id, 'pdf_no_data'), alert=True)
            return

        elif data == "pdf_date_wise":
            from bot.handlers.pdf import PDFHandler
            PDFHandler.user_states[user_id] = "ST_PDF_DATE"
            await event.edit(t(user_id, 'pdf_date_prompt'),
                           buttons=[Button.inline(t(user_id, 'back'), b"pdf_main")])
            return

        # ==================== RESET HANDLERS ====================
        elif data.startswith("reset_"):
            mode = data.split("_")[1]
            if mode == "month":
                confirm_buttons = [[Button.inline(t(user_id, 'confirm'), b"conf_month_yes"),
                                   Button.inline(t(user_id, 'no'), b"conf_no")]]
                await event.edit(t(user_id, 'reset_month_confirm', month_key), buttons=confirm_buttons)
            return

        elif data == "conf_no":
            from bot.handlers.message import MessageHandler
            MessageHandler.user_states.pop(user_id, None)
            await event.edit(t(user_id, 'operation_cancelled'))
            return

        elif data == "conf_month_yes":
            BalanceRepository.delete_month_data(user_id, month_key)
            await event.edit(t(user_id, 'reset_month_success', month_key))
            return

        # ==================== REPORT HANDLERS ====================
        elif data == "rep_today":
            today = get_current_date(event)
            db_data = get_user_monthly_data(user_id, month_key)
            today_income = sum(e['amount'] for e in db_data['history']
                              if e.get('date') == today and e['amount'] > 0
                              and (not e.get("is_debt_logic") or e.get("is_outstanding_repay")))
            today_expense = sum(abs(e['amount']) for e in db_data['history']
                               if e.get('date') == today and e['amount'] < 0
                               and (not e.get("is_debt_logic") or e.get("is_outstanding_repay")))
            await event.edit(
                f"{t(user_id, 'today_report', today)}\n━━━━━━━━━━━━━━━━━━\n"
                f"{t(user_id, 'total_income')}: {today_income:.2f}\n"
                f"{t(user_id, 'total_expense')}: {today_expense:.2f}\n"
                f"{t(user_id, 'net')}: {(today_income - today_expense):.2f}",
                buttons=[Button.inline(t(user_id, 'back'), b"rep_main")]
            )
            return

        elif data == "rep_date":
            from bot.handlers.message import MessageHandler
            MessageHandler.user_states[user_id] = "ST_REP_DATE"
            await event.edit(t(user_id, 'enter_date'),
                           buttons=[Button.inline(t(user_id, 'cancel'), b"rep_main")])
            return

        elif data == "rep_main":
            from bot.handlers.message import MessageHandler
            MessageHandler.user_states.pop(user_id, None)
            buttons = [
                [Button.inline(t(user_id, 'today_income_expenses'), b"rep_today")],
                [Button.inline(t(user_id, 'date_wise'), b"rep_date")],
                [Button.inline(t(user_id, 'monthly_wise'), b"mrep_0")],
                [Button.inline(t(user_id, 'cancel'), b"cancel_state")]
            ]
            await event.edit(t(user_id, 'select_report'), buttons=buttons)
            return

        elif data.startswith("mrep_"):
            from bot.handlers.report import ReportHandler
            page_idx = int(data.split("_")[1])
            rh = ReportHandler(self.client)
            await rh.send_monthly_summary_page(user_id, event.chat_id, page_idx, event.message_id)
            return

        elif data == "cancel_state":
            from bot.handlers.message import MessageHandler
            MessageHandler.user_states.pop(user_id, None)
            await event.edit(t(user_id, 'operation_cancelled'))
            return

        # ==================== HISTORY ====================
        elif data.startswith("hist_"):
            from bot.handlers.history import HistoryHandler
            page = int(data.split("_")[1])
            hh = HistoryHandler(self.client)
            await hh.send_history_page(user_id, event.chat_id, page, event.message_id)
            return

        # ==================== DEBT MAIN MENU ====================
        elif data == "debt_main_menu":
            from bot.handlers.message import MessageHandler
            MessageHandler.user_states.pop(user_id, None)
            buttons = [
                [Button.inline(t(user_id, 'give'), b"debt_give_0"),
                 Button.inline(t(user_id, 'take'), b"debt_take_0")],
                [Button.inline(t(user_id, 'i_repaid'), b"debt_i_repaid"),
                 Button.inline(t(user_id, 'he_repaid'), b"debt_he_repaid")],
                [Button.inline(t(user_id, 'debt_list'), b"debt_list")],
                [Button.inline(t(user_id, 'outstanding'), b"out_main")],
                [Button.inline(t(user_id, 'cancel'), b"cancel_state")]
            ]
            await event.edit(t(user_id, 'debt_manager') + "\n" + t(user_id, 'select_option'), buttons=buttons)
            return

        # ==================== OUTSTANDING HANDLERS ====================
        elif data == "out_main":
            from bot.handlers.debt import DebtHandler
            dh = DebtHandler(self.client)
            await dh.show_outstanding_menu(event)
            return

        elif data.startswith("out_give_") or data.startswith("out_take_"):
            dtype = "give" if "give" in data else "take"
            page = int(data.split("_")[2])
            await self.show_out_names(event, dtype, page)
            return

        elif data.startswith("out_irep_") or data.startswith("out_herep_"):
            dtype = "take" if "irep" in data else "give"
            page = int(data.split("_")[2])
            await self.show_out_repay_list(event, dtype, page)
            return

        elif data == "out_list":
            await self.show_out_grid(event)
            return

        elif data.startswith("osel_"):
            parts = data.split("_")
            dtype = parts[1]
            name = parts[2]
            from bot.handlers.message import MessageHandler
            MessageHandler.user_states[user_id] = f"ST_OUTAMT_{dtype}_{name}"
            action = t(user_id, 'to_give') if dtype == 'give' else t(user_id, 'to_take')
            await event.edit(t(user_id, 'enter_out_amount', name, action),
                           buttons=[Button.inline(t(user_id, 'back'), b"out_main")])
            return

        elif data.startswith("onew_"):
            dtype = data.split("_")[1]
            from bot.handlers.message import MessageHandler
            MessageHandler.user_states[user_id] = f"ST_OUTNEW_{dtype}"
            await event.edit(t(user_id, 'add_new_person'),
                           buttons=[Button.inline(t(user_id, 'back'), b"out_main")])
            return

        elif data.startswith("orp_"):
            parts = data.split("_")
            dtype = parts[1]
            d_id = parts[2]
            from bot.handlers.message import MessageHandler
            MessageHandler.user_states[user_id] = f"ST_OUTREPAY_{d_id}"
            await event.edit(t(user_id, 'enter_out_amount', '', ''),
                           buttons=[Button.inline(t(user_id, 'back'), b"out_main")])
            return

        elif data.startswith("ovdet_"):
            name = data.split("_")[1]
            await self.show_out_person_history(event, name, 0)
            return

        # ==================== DEBT GIVE/TAKE HANDLERS ====================
        elif data.startswith("debt_give_") or data.startswith("debt_take_"):
            dtype = "give" if "give" in data else "take"
            page = int(data.split("_")[2]) if len(data.split("_")) > 2 else 0
            await self.show_debt_names(event, dtype, page)
            return

        elif data.startswith("dsel_"):
            parts = data.split("_")
            dtype = parts[1]
            name = parts[2]
            from bot.handlers.message import MessageHandler
            MessageHandler.user_states[user_id] = f"ST_AMT_{dtype}_{name}"
            action = t(user_id, 'to_give') if dtype == 'give' else t(user_id, 'to_take')
            await event.edit(t(user_id, 'enter_amount', name, action),
                           buttons=[Button.inline(t(user_id, 'back'), f"debt_{dtype}_0")])
            return

        elif data.startswith("dnew_"):
            dtype = data.split("_")[1]
            from bot.handlers.message import MessageHandler
            MessageHandler.user_states[user_id] = f"ST_NEW_{dtype}"
            await event.edit(t(user_id, 'add_new_person'),
                           buttons=[Button.inline(t(user_id, 'back'), f"debt_{dtype}_0")])
            return

        elif data == "debt_i_repaid":
            await self.show_repay_list(event, "take", 0)
            return

        elif data == "debt_he_repaid":
            await self.show_repay_list(event, "give", 0)
            return

        elif data.startswith("rpl_"):
            parts = data.split("_")
            dtype = parts[1]
            page = int(parts[2])
            await self.show_repay_list(event, dtype, page)
            return

        elif data == "debt_list":
            await self.show_debt_grid(event)
            return

        elif data.startswith("rp_"):
            parts = data.split("_")
            dtype = parts[1]
            debt_id = int(parts[2])
            debt = DebtRepository.get_by_id(debt_id)
            if debt:
                from bot.handlers.message import MessageHandler
                MessageHandler.user_states[user_id] = f"ST_REPAY_AMT_{dtype}_{debt_id}_{debt['name']}"
                await event.edit(t(user_id, 'enter_amount', debt['name'], ''),
                               buttons=[Button.inline(t(user_id, 'back'), b"debt_main_menu")])
            return

        elif data.startswith("vdet_"):
            name = data.split("_")[1]
            await self.show_person_history(event, name, 0)
            return

        elif data.startswith("phist_"):
            parts = data.split("_")
            name = parts[1]
            page = int(parts[2])
            await self.show_person_history(event, name, page)
            return

        elif data.startswith("deldebt_"):
            name = data.split("_")[1]
            btns = [[Button.inline(t(user_id, 'confirm'), f"confdeldebt_{name}"),
                    Button.inline(t(user_id, 'no'), f"vdet_{name}")]]
            await event.edit(t(user_id, 'delete_confirm', name), buttons=btns)
            return

        elif data.startswith("confdeldebt_"):
            name = data.split("_")[1]
            DebtRepository.delete_by_name(user_id, name)
            DebtHistoryRepository.delete_by_name(user_id, name)
            await event.edit(t(user_id, 'deleted', name),
                           buttons=[Button.inline(t(user_id, 'back'), b"debt_list")])
            return

        # ==================== GOAL HANDLERS ====================
        elif data == "goal_main":
            from bot.handlers.message import MessageHandler
            MessageHandler.user_states.pop(user_id, None)
            from bot.handlers.goal import GoalHandler
            gh = GoalHandler(self.client)
            await gh.show_goal_menu(event)
            return

        elif data.startswith("glist_"):
            page = int(data.split("_")[1])
            await self.show_goal_list(event, page)
            return

        elif data.startswith("gsave_"):
            gname = data.split("_")[1]
            from bot.handlers.message import MessageHandler
            MessageHandler.user_states[user_id] = f"ST_SAVE_GOAL_{gname}"
            btns = [[Button.inline(t(user_id, 'delete_goal_confirm', ''), f"delgoal_{gname}")],
                    [Button.inline(t(user_id, 'back'), b"glist_0")]]
            await event.edit(t(user_id, 'enter_save_amount', gname), buttons=btns)
            return

        elif data.startswith("delgoal_"):
            gname = data.split("_")[1]
            btns = [[Button.inline(t(user_id, 'confirm'), f"confdelgoal_{gname}"),
                    Button.inline(t(user_id, 'no'), f"gsave_{gname}")]]
            await event.edit(t(user_id, 'delete_goal_confirm', gname), buttons=btns)
            return

        elif data.startswith("confdelgoal_"):
            gname = data.split("_")[1]
            GoalRepository.delete_by_name(user_id, gname)
            GoalHistoryRepository.delete_by_name(user_id, gname)
            await event.edit(t(user_id, 'goal_deleted', gname),
                           buttons=[Button.inline(t(user_id, 'back'), b"glist_0")])
            return

        elif data.startswith("gdet_"):
            page = int(data.split("_")[1])
            await self.show_goal_details_menu(event, page)
            return

        elif data.startswith("vgoal_"):
            gname = data.split("_")[1]
            await self.show_goal_history(event, gname, 0)
            return

        elif data == "new_goal":
            from bot.handlers.message import MessageHandler
            MessageHandler.user_states[user_id] = "ST_NEW_GOAL"
            await event.edit(t(user_id, 'enter_goal'),
                           buttons=[Button.inline(t(user_id, 'back'), b"goal_main")])
            return

        # ==================== TRANSFER HANDLERS ====================
        elif data.startswith("t_from_"):
            page = int(data.split("_")[2])
            await self.show_transfer_wallets(event, page, "from")
            return

        elif data.startswith("tsel_f_"):
            wallet_from = data.replace("tsel_f_", "")
            await self.show_transfer_wallets(event, 0, "to", wallet_from)
            return

        elif data.startswith("t_to_"):
            parts = data.split("_")
            page = int(parts[2])
            wallet_from = parts[3]
            await self.show_transfer_wallets(event, page, "to", wallet_from)
            return

        elif data.startswith("tsel_t_"):
            parts = data.split("_")
            wallet_from = parts[2]
            wallet_to = parts[3]
            from bot.handlers.message import MessageHandler
            MessageHandler.user_states[user_id] = f"ST_TRNS_AMT_{wallet_from}_{wallet_to}"
            await event.edit(t(user_id, 'enter_transfer_amount', wallet_from, wallet_to),
                           buttons=[[Button.inline(t(user_id, 'back'), f"tsel_f_{wallet_from}")],
                                   [Button.inline(t(user_id, 'cancel'), b"cancel_state")]])
            return

        # ==================== WALLET DELETE HANDLERS ====================
        elif data.startswith("dw_list_"):
            page = int(data.split("_")[2])
            await self.show_del_wallet_list(event, page)
            return

        elif data.startswith("dw_sel_"):
            w_name = data.split("_")[2]
            btns = [[Button.inline(t(user_id, 'confirm'), f"dw_conf_{w_name}"),
                    Button.inline(t(user_id, 'no'), b"dw_list_0")]]
            await event.edit(t(user_id, 'delete_wallet_confirm', w_name), buttons=btns)
            return

        elif data.startswith("dw_conf_"):
            w_name = data.split("_")[2]
            data_m = get_user_monthly_data(user_id, month_key)
            wallets = data_m.get('wallets', {})
            if w_name in wallets:
                del wallets[w_name]
                BalanceRepository.update_monthly_data(user_id, month_key, data_m)
                await event.edit(t(user_id, 'wallet_deleted', w_name),
                               buttons=[Button.inline(t(user_id, 'back'), b"dw_list_0")])
            else:
                await event.answer(t(user_id, 'no_data'), alert=True)
            return

        # ==================== CONFIRMATION HANDLERS ====================
        elif data == "conf_reset_full":
            await self.reset_full_database(event)
            return

        # ==================== OUTSTANDING DELETE HANDLERS ====================
        elif data.startswith("delout_"):
            name = data.split("_")[1]
            btns = [[Button.inline(t(user_id, 'confirm'), f"confdelout_{name}"),
                    Button.inline(t(user_id, 'no'), f"ovdet_{name}")]]
            await event.edit(t(user_id, 'delete_out_confirm', name), buttons=btns)
            return

        elif data.startswith("confdelout_"):
            name = data.split("_")[1]
            OutstandingRepository.delete_by_name(user_id, name)
            OutstandingHistoryRepository.delete_by_name(user_id, name)
            await event.edit(t(user_id, 'out_deleted', name),
                           buttons=[Button.inline(t(user_id, 'back'), b"out_list")])
            return

    # ==================== HELPER METHODS ====================

    async def show_out_names(self, event, dtype, page):
        """Show names for outstanding (give_work/take_work)"""
        user_id = event.sender_id
        all_docs = OutstandingRepository.get_by_type(user_id, dtype)
        all_names = list(set([d['name'] for d in all_docs]))
        total_pages = max(1, math.ceil(len(all_names) / 10))
        start = page * 10
        names_slice = all_names[start:start + 10]

        btns = [[Button.inline(name, f"osel_{dtype}_{name}")] for name in names_slice]

        nav = []
        if page > 0:
            nav.append(Button.inline(t(user_id, 'previous'), f"out_{dtype}_{page-1}"))
        if (page + 1) < total_pages:
            nav.append(Button.inline(t(user_id, 'next'), f"out_{dtype}_{page+1}"))
        if nav:
            btns.append(nav)

        btns.append([Button.inline(t(user_id, 'add_new_person'), f"onew_{dtype}"),
                    Button.inline(t(user_id, 'back'), b"out_main")])

        await event.edit(f"{t(user_id, 'select_name_work')}\n{t(user_id, 'page')}: {page+1}/{total_pages}",
                        buttons=btns)

    async def show_out_repay_list(self, event, dtype, page):
        """Show repayment list for outstanding (i_repaid_work/he_repaid_work)"""
        user_id = event.sender_id
        rows = OutstandingRepository.get_by_type(user_id, dtype)
        rows = [r for r in rows if r['amount'] > 0]

        if not rows:
            await event.answer(t(user_id, 'no_list_alert'), alert=True)
            return

        total_pages = max(1, math.ceil(len(rows) / 10))
        start = page * 10
        slice_rows = rows[start:start + 10]

        btns = [[Button.inline(f"{r['name']} ({r['amount']:.2f})", f"orp_{dtype}_{r['id']}")] for r in slice_rows]

        nav = []
        if page > 0:
            nav.append(Button.inline(t(user_id, 'previous'), f"out_{'irep' if dtype=='take' else 'herep'}_{page-1}"))
        if (page + 1) < total_pages:
            nav.append(Button.inline(t(user_id, 'next'), f"out_{'irep' if dtype=='take' else 'herep'}_{page+1}"))
        if nav:
            btns.append(nav)

        btns.append([Button.inline(t(user_id, 'back'), b"out_main")])

        await event.edit(f"{t(user_id, 'repay_list_work')}\n{t(user_id, 'page')}: {page+1}/{total_pages}",
                        buttons=btns)

    async def show_out_grid(self, event):
        """Show outstanding grid (give on left, take on right)"""
        user_id = event.sender_id
        give_list = OutstandingRepository.get_by_type(user_id, "give")
        take_list = OutstandingRepository.get_by_type(user_id, "take")

        buttons = []
        max_len = max(len(give_list), len(take_list))

        for i in range(max_len):
            row = []
            if i < len(give_list):
                d = give_list[i]
                row.append(Button.inline(f"⬆️ {d['name']} {d['amount']:.2f}", f"ovdet_{d['name']}"))
            else:
                row.append(Button.inline("-", b"noop"))

            if i < len(take_list):
                d = take_list[i]
                row.append(Button.inline(f"⬇️ {d['name']} {d['amount']:.2f}", f"ovdet_{d['name']}"))
            else:
                row.append(Button.inline("-", b"noop"))

            buttons.append(row)

        buttons.append([Button.inline(t(user_id, 'back'), b"out_main")])
        await event.edit(t(user_id, 'out_grid'), buttons=buttons)

    async def show_out_person_history(self, event, name, page):
        """Show transaction history for a person in outstanding"""
        user_id = event.sender_id
        logs = OutstandingHistoryRepository.get_by_name(user_id, name)
        total_logs = len(logs)
        start = page * 10
        slice_logs = logs[start:start + 10]
        total_pages = max(1, math.ceil(total_logs / 10))

        msg = f"{t(user_id, 'out_history', name)}\n━━━━━━━━━━━━━━━━━━\n"
        if not slice_logs:
            msg += t(user_id, 'no_transactions')
        for l in slice_logs:
            msg += f"🔹 {l['amount']:.2f} | {l['date']} | {l['time']}\n"

        btns = [[Button.inline(t(user_id, 'back'), b"out_list"),
                Button.inline(t(user_id, 'delete'), f"delout_{name}")]]

        await event.edit(msg, buttons=btns)

    async def show_debt_names(self, event, dtype, page):
        """Show names for debt (give/take)"""
        user_id = event.sender_id
        all_names = DebtRepository.get_distinct_names(user_id, dtype)
        total_pages = max(1, math.ceil(len(all_names) / 10))
        start = page * 10
        names_slice = all_names[start:start + 10]

        btns = [[Button.inline(name, f"dsel_{dtype}_{name}")] for name in names_slice]

        nav = []
        if page > 0:
            nav.append(Button.inline(t(user_id, 'previous'), f"debt_{dtype}_{page-1}"))
        if (page + 1) < total_pages:
            nav.append(Button.inline(t(user_id, 'next'), f"debt_{dtype}_{page+1}"))
        if nav:
            btns.append(nav)

        action = t(user_id, 'will_receive') if dtype == 'give' else t(user_id, 'will_pay')
        btns.append([Button.inline(t(user_id, 'add_new_person'), f"dnew_{dtype}"),
                    Button.inline(t(user_id, 'back'), b"debt_main_menu")])

        await event.edit(f"{t(user_id, 'select_person', action)}\n{t(user_id, 'page')}: {page+1}/{total_pages}",
                        buttons=btns)

    async def show_repay_list(self, event, dtype, page):
        """Show repayment list for debt (i_repaid/he_repaid)"""
        user_id = event.sender_id
        rows = DebtRepository.get_by_type(user_id, dtype)
        rows = [r for r in rows if r['amount'] > 0]

        if not rows:
            await event.answer(t(user_id, 'no_list_alert'), alert=True)
            return

        total_pages = max(1, math.ceil(len(rows) / 10))
        start = page * 10
        slice_rows = rows[start:start + 10]

        btns = [[Button.inline(f"{r['name']} ({r['amount']:.2f})", f"rp_{dtype}_{r['id']}")] for r in slice_rows]

        nav = []
        if page > 0:
            nav.append(Button.inline(t(user_id, 'previous'), f"rpl_{dtype}_{page-1}"))
        if (page + 1) < total_pages:
            nav.append(Button.inline(t(user_id, 'next'), f"rpl_{dtype}_{page+1}"))
        if nav:
            btns.append(nav)

        btns.append([Button.inline(t(user_id, 'back'), b"debt_main_menu")])

        await event.edit(f"{t(user_id, 'repay_list')}\n{t(user_id, 'page')}: {page+1}/{total_pages}",
                        buttons=btns)

    async def show_debt_grid(self, event):
        """Show debt grid (receivable on left, payable on right)"""
        user_id = event.sender_id
        give_list = DebtRepository.get_by_type(user_id, "give")
        take_list = DebtRepository.get_by_type(user_id, "take")

        buttons = []
        max_len = max(len(give_list), len(take_list))

        for i in range(max_len):
            row = []
            if i < len(give_list):
                d = give_list[i]
                row.append(Button.inline(f"⬆️ {d['name']} {d['amount']:.2f}", f"vdet_{d['name']}"))
            else:
                row.append(Button.inline("-", b"noop"))

            if i < len(take_list):
                d = take_list[i]
                row.append(Button.inline(f"⬇️ {d['name']} {d['amount']:.2f}", f"vdet_{d['name']}"))
            else:
                row.append(Button.inline("-", b"noop"))

            buttons.append(row)

        buttons.append([Button.inline(t(user_id, 'back'), b"debt_main_menu")])
        await event.edit(t(user_id, 'debt_grid'), buttons=buttons)

    async def show_person_history(self, event, name, page):
        """Show transaction history for a person in debt"""
        user_id = event.sender_id
        logs, total_logs = DebtHistoryRepository.get_by_name(user_id, name, limit=10, offset=page * 10)
        total_pages = max(1, math.ceil(total_logs / 10))

        msg = f"{t(user_id, 'person_history', name)}\n━━━━━━━━━━━━━━━━━━\n"
        msg += f"{t(user_id, 'page')}: {page + 1} / {total_pages}\n\n"
        if not logs:
            msg += t(user_id, 'no_transactions')
        for l in logs:
            msg += f"🔹 {l['amount']:.2f} | {l['date']} | {l['time']}\n"

        nav = []
        if page > 0:
            nav.append(Button.inline(t(user_id, 'previous'), f"phist_{name}_{page-1}"))
        if (page + 1) < total_pages:
            nav.append(Button.inline(t(user_id, 'next'), f"phist_{name}_{page+1}"))

        btns = []
        if nav:
            btns.append(nav)
        btns.append([Button.inline(t(user_id, 'back'), b"debt_list"),
                    Button.inline(t(user_id, 'delete'), f"deldebt_{name}")])

        await event.edit(msg, buttons=btns)

    async def show_goal_list(self, event, page):
        """Show list of goals"""
        user_id = event.sender_id
        rows = GoalRepository.get_all(user_id)
        total_pages = max(1, math.ceil(len(rows) / 10))
        start = page * 10
        slice_rows = rows[start:start + 10]

        btns = [[Button.inline(f"{r['name']} ({r['saved']:.0f}/{r['target']:.0f})", f"gsave_{r['name']}")] for r in slice_rows]

        nav = []
        if page > 0:
            nav.append(Button.inline(t(user_id, 'previous'), f"glist_{page-1}"))
        if (page + 1) < total_pages:
            nav.append(Button.inline(t(user_id, 'next'), f"glist_{page+1}"))
        if nav:
            btns.append(nav)

        btns.append([Button.inline(t(user_id, 'add_new_goal'), b"new_goal"),
                    Button.inline(t(user_id, 'back'), b"goal_main")])

        await event.edit(f"{t(user_id, 'your_goals')}\n{t(user_id, 'page')}: {page+1}/{total_pages}",
                        buttons=btns)

    async def show_goal_details_menu(self, event, page):
        """Show goal progress percentages"""
        user_id = event.sender_id
        rows = GoalRepository.get_all(user_id)

        btns = []
        for r in rows:
            percent = (r['saved'] / r['target'] * 100) if r['target'] > 0 else 0
            btns.append([Button.inline(f"🎯 {r['name']} {percent:.0f}%", f"vgoal_{r['name']}")])

        btns.append([Button.inline(t(user_id, 'back'), b"goal_main")])
        await event.edit(t(user_id, 'goal_progress'), buttons=btns)

    async def show_goal_history(self, event, gname, page):
        """Show transaction history for a goal"""
        user_id = event.sender_id
        logs = GoalHistoryRepository.get_by_name(user_id, gname, limit=10)

        msg = f"{t(user_id, 'goal_detail', gname)}\n━━━━━━━━━━━━━\n"
        if not logs:
            msg += t(user_id, 'no_savings')
        for l in logs:
            msg += f"🔹 {l['amount']:.2f} | {l['date']} | {l['time']}\n"

        await event.edit(msg, buttons=[[Button.inline(t(user_id, 'back'), b"gdet_0")]])

    async def show_transfer_wallets(self, event, page, mode, wallet_from=None):
        """Show wallet selection for transfer"""
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

        if not all_wallets:
            await event.edit(t(user_id, 'no_wallet'))
            return

        page_size = 10
        total_pages = max(1, math.ceil(len(all_wallets) / page_size))
        start = page * page_size
        wallets_slice = all_wallets[start:start + page_size]

        msg = f"{msg_header}\n━━━━━━━━━━━━━━━━━━\n{t(user_id, 'page')}: {page + 1} / {total_pages}"
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
        except Exception:
            await event.respond(msg, buttons=btns)

    async def show_del_wallet_list(self, event, page):
        """Show list of wallets for deletion"""
        user_id = event.sender_id
        data = get_user_monthly_data(user_id, get_current_month(event))
        wallets = data.get('wallets', {})
        all_wallets = list(wallets.keys())

        if not all_wallets:
            await event.respond(t(user_id, 'no_wallet'))
            return

        page_size = 10
        total_pages = max(1, math.ceil(len(all_wallets) / page_size))
        start = page * page_size
        wallets_slice = all_wallets[start:start + page_size]

        msg = f"{t(user_id, 'select_wallet_delete')}\n{t(user_id, 'page')}: {page + 1} / {total_pages}"
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
        except Exception:
            await event.respond(msg, buttons=btns)

    async def reset_full_database(self, event):
        """Reset all user data"""
        user_id = event.sender_id
        BalanceRepository.delete_user_data(user_id)
        DebtRepository.delete_user_data(user_id)
        DebtHistoryRepository.delete_user_data(user_id)
        GoalRepository.delete_user_data(user_id)
        GoalHistoryRepository.delete_user_data(user_id)
        OutstandingRepository.delete_user_data(user_id)
        OutstandingHistoryRepository.delete_user_data(user_id)
        await event.edit(t(user_id, 'reset_all_success'))
