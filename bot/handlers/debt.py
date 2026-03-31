"""
Debt Handler - লোন ও ধার ম্যানেজারের জন্য হ্যান্ডলার
"""
from bot.handlers.base import BaseHandler
from bot.utils.translations import t
from telethon import Button

class DebtHandler(BaseHandler):
    """
    Debt Manager Handler
    Handles /debt command and its sub-menus
    """
    
    async def show_debt_menu(self, event):
        """
        ডেব্ট ম্যানেজারের মূল মেনু দেখায়
        """
        user_id = event.sender_id
        
        buttons = [
            [
                Button.inline(t(user_id, 'give'), b"debt_give_0"),
                Button.inline(t(user_id, 'take'), b"debt_take_0")
            ],
            [
                Button.inline(t(user_id, 'i_repaid'), b"debt_i_repaid"),
                Button.inline(t(user_id, 'he_repaid'), b"debt_he_repaid")
            ],
            [
                Button.inline(t(user_id, 'debt_list'), b"debt_list")
            ],
            [
                Button.inline(t(user_id, 'outstanding'), b"out_main")
            ],
            [
                Button.inline(t(user_id, 'cancel'), b"cancel_state")
            ]
        ]
        
        await event.respond(
            t(user_id, 'debt_manager'),
            buttons=buttons
        )
    
    async def show_give_menu(self, event, page=0):
        """
        'দিয়েছি' অপশনের জন্য নামের তালিকা দেখায়
        """
        user_id = event.sender_id
        from bot.database.repositories import DebtRepository
        
        all_names = DebtRepository.get_distinct_names(user_id, "give")
        total_pages = max(1, (len(all_names) + 9) // 10)
        start = page * 10
        names_slice = all_names[start:start + 10]
        
        buttons = []
        for name in names_slice:
            buttons.append([Button.inline(name, f"dsel_give_{name}")])
        
        # Navigation buttons
        nav_buttons = []
        if page > 0:
            nav_buttons.append(Button.inline(t(user_id, 'previous'), f"debt_give_{page-1}"))
        if page + 1 < total_pages:
            nav_buttons.append(Button.inline(t(user_id, 'next'), f"debt_give_{page+1}"))
        if nav_buttons:
            buttons.append(nav_buttons)
        
        # Add new person and back buttons
        buttons.append([
            Button.inline(t(user_id, 'add_new_person'), f"dnew_give"),
            Button.inline(t(user_id, 'back'), b"debt_main_menu")
        ])
        
        action = t(user_id, 'will_receive')
        await event.edit(
            f"{t(user_id, 'select_person', action)}\n"
            f"{t(user_id, 'page')}: {page + 1} / {total_pages}",
            buttons=buttons
        )
    
    async def show_take_menu(self, event, page=0):
        """
        'নিয়েছি' অপশনের জন্য নামের তালিকা দেখায়
        """
        user_id = event.sender_id
        from bot.database.repositories import DebtRepository
        
        all_names = DebtRepository.get_distinct_names(user_id, "take")
        total_pages = max(1, (len(all_names) + 9) // 10)
        start = page * 10
        names_slice = all_names[start:start + 10]
        
        buttons = []
        for name in names_slice:
            buttons.append([Button.inline(name, f"dsel_take_{name}")])
        
        # Navigation buttons
        nav_buttons = []
        if page > 0:
            nav_buttons.append(Button.inline(t(user_id, 'previous'), f"debt_take_{page-1}"))
        if page + 1 < total_pages:
            nav_buttons.append(Button.inline(t(user_id, 'next'), f"debt_take_{page+1}"))
        if nav_buttons:
            buttons.append(nav_buttons)
        
        # Add new person and back buttons
        buttons.append([
            Button.inline(t(user_id, 'add_new_person'), f"dnew_take"),
            Button.inline(t(user_id, 'back'), b"debt_main_menu")
        ])
        
        action = t(user_id, 'will_pay')
        await event.edit(
            f"{t(user_id, 'select_person', action)}\n"
            f"{t(user_id, 'page')}: {page + 1} / {total_pages}",
            buttons=buttons
        )
    
    async def show_repay_list(self, event, debt_type, page=0):
        """
        পরিশোধের জন্য তালিকা দেখায়
        debt_type: 'give' (he_repaid) বা 'take' (i_repaid)
        """
        user_id = event.sender_id
        from bot.database.repositories import DebtRepository
        
        # Get debts with amount > 0
        all_debts = DebtRepository.get_by_type(user_id, debt_type)
        active_debts = [d for d in all_debts if d['amount'] > 0]
        
        if not active_debts:
            await event.answer(t(user_id, 'no_list_alert'), alert=True)
            return
        
        total_pages = max(1, (len(active_debts) + 9) // 10)
        start = page * 10
        slice_debts = active_debts[start:start + 10]
        
        buttons = []
        for debt in slice_debts:
            buttons.append([
                Button.inline(
                    f"{debt['name']} ({debt['amount']:.2f})",
                    f"rp_{debt_type}_{debt['id']}"
                )
            ])
        
        # Navigation buttons
        nav_buttons = []
        if page > 0:
            callback = f"rpl_{debt_type}_{page-1}"
            nav_buttons.append(Button.inline(t(user_id, 'previous'), callback))
        if page + 1 < total_pages:
            callback = f"rpl_{debt_type}_{page+1}"
            nav_buttons.append(Button.inline(t(user_id, 'next'), callback))
        if nav_buttons:
            buttons.append(nav_buttons)
        
        # Back button
        buttons.append([
            Button.inline(t(user_id, 'back'), b"debt_main_menu")
        ])
        
        await event.edit(
            f"{t(user_id, 'repay_list')}\n"
            f"{t(user_id, 'page')}: {page + 1} / {total_pages}",
            buttons=buttons
        )
    
    async def show_debt_grid(self, event):
        """
        পাওনা ও দেনার গ্রিড দেখায় (বামে পাওনা, ডানে দেনা)
        """
        user_id = event.sender_id
        from bot.database.repositories import DebtRepository
        
        receivable = DebtRepository.get_by_type(user_id, "give")
        payable = DebtRepository.get_by_type(user_id, "take")
        
        buttons = []
        max_len = max(len(receivable), len(payable))
        
        for i in range(max_len):
            row = []
            
            # Left side - Receivable (পাওনা)
            if i < len(receivable):
                d = receivable[i]
                row.append(Button.inline(
                    f"⬆️ {d['name']} {d['amount']:.2f}",
                    f"vdet_{d['name']}"
                ))
            else:
                row.append(Button.inline("-", b"noop"))
            
            # Right side - Payable (দেনা)
            if i < len(payable):
                d = payable[i]
                row.append(Button.inline(
                    f"⬇️ {d['name']} {d['amount']:.2f}",
                    f"vdet_{d['name']}"
                ))
            else:
                row.append(Button.inline("-", b"noop"))
            
            buttons.append(row)
        
        # Back button
        buttons.append([
            Button.inline(t(user_id, 'back'), b"debt_main_menu")
        ])
        
        await event.edit(t(user_id, 'debt_grid'), buttons=buttons)
    
    async def show_person_history(self, event, name, page=0):
        """
        নির্দিষ্ট ব্যক্তির সাথে লেনদেনের ইতিহাস দেখায়
        """
        user_id = event.sender_id
        from bot.database.repositories import DebtHistoryRepository
        
        # Get history with pagination
        history, total_logs = DebtHistoryRepository.get_by_name(
            user_id, name, limit=10, offset=page * 10
        )
        
        total_pages = max(1, (total_logs + 9) // 10)
        
        msg = f"{t(user_id, 'person_history', name)}\n"
        msg += "━━━━━━━━━━━━━━━━━━\n"
        msg += f"{t(user_id, 'page')}: {page + 1} / {total_pages}\n\n"
        
        if not history:
            msg += t(user_id, 'no_transactions')
        else:
            for h in history:
                icon = "💰" if h['amount'] > 0 else "💸"
                msg += f"{icon} {h['amount']:+.2f} | {h['date']} | {h['time']}\n"
        
        # Navigation buttons
        buttons = []
        nav_buttons = []
        
        if page > 0:
            nav_buttons.append(Button.inline(
                t(user_id, 'previous'),
                f"phist_{name}_{page-1}"
            ))
        if page + 1 < total_pages:
            nav_buttons.append(Button.inline(
                t(user_id, 'next'),
                f"phist_{name}_{page+1}"
            ))
        
        if nav_buttons:
            buttons.append(nav_buttons)
        
        # Back and delete buttons
        buttons.append([
            Button.inline(t(user_id, 'back'), b"debt_list"),
            Button.inline(t(user_id, 'delete'), f"deldebt_{name}")
        ])
        
        await event.edit(msg, buttons=buttons)
    
    async def delete_person_data(self, event, name):
        """
        নির্দিষ্ট ব্যক্তির সব ডেব্ট ডাটা ডিলিট করে
        """
        user_id = event.sender_id
        from bot.database.repositories import DebtRepository, DebtHistoryRepository
        
        # Delete debt data
        DebtRepository.delete_by_name(user_id, name)
        DebtHistoryRepository.delete_by_name(user_id, name)
        
        await event.edit(
            t(user_id, 'deleted', name),
            buttons=[Button.inline(t(user_id, 'back'), b"debt_list")]
        )
    
    async def show_outstanding_menu(self, event):
        """
        আউটস্ট্যান্ডিং পেমেন্ট ম্যানেজারের মেনু দেখায়
        """
        user_id = event.sender_id
        
        buttons = [
            [
                Button.inline(t(user_id, 'give_work'), b"out_give_0"),
                Button.inline(t(user_id, 'take_work'), b"out_take_0")
            ],
            [
                Button.inline(t(user_id, 'i_repaid_work'), b"out_irep_0"),
                Button.inline(t(user_id, 'he_repaid_work'), b"out_herep_0")
            ],
            [
                Button.inline(t(user_id, 'debt_list_work'), b"out_list")
            ],
            [
                Button.inline(t(user_id, 'back'), b"debt_main_menu")
            ]
        ]
        
        await event.edit(t(user_id, 'out_manager'), buttons=buttons)
    
    async def show_out_names(self, event, debt_type, page=0):
        """
        আউটস্ট্যান্ডিং এর জন্য নামের তালিকা দেখায়
        """
        user_id = event.sender_id
        from bot.database.repositories import OutstandingRepository
        
        all_names = OutstandingRepository.get_distinct_names(user_id, debt_type)
        total_pages = max(1, (len(all_names) + 9) // 10)
        start = page * 10
        names_slice = all_names[start:start + 10]
        
        buttons = []
        for name in names_slice:
            buttons.append([Button.inline(name, f"osel_{debt_type}_{name}")])
        
        # Navigation buttons
        nav_buttons = []
        if page > 0:
            nav_buttons.append(Button.inline(
                t(user_id, 'previous'),
                f"out_{debt_type}_{page-1}"
            ))
        if page + 1 < total_pages:
            nav_buttons.append(Button.inline(
                t(user_id, 'next'),
                f"out_{debt_type}_{page+1}"
            ))
        if nav_buttons:
            buttons.append(nav_buttons)
        
        # Add new person and back buttons
        buttons.append([
            Button.inline(t(user_id, 'add_new_person'), f"onew_{debt_type}"),
            Button.inline(t(user_id, 'back'), b"out_main")
        ])
        
        await event.edit(
            f"{t(user_id, 'select_name_work')}\n"
            f"{t(user_id, 'page')}: {page + 1} / {total_pages}",
            buttons=buttons
        )
    
    async def show_out_repay_list(self, event, debt_type, page=0):
        """
        আউটস্ট্যান্ডিং পরিশোধের জন্য তালিকা দেখায়
        """
        user_id = event.sender_id
        from bot.database.repositories import OutstandingRepository
        
        all_out = OutstandingRepository.get_by_type(user_id, debt_type)
        active_out = [o for o in all_out if o['amount'] > 0]
        
        if not active_out:
            await event.answer(t(user_id, 'no_list_alert'), alert=True)
            return
        
        total_pages = max(1, (len(active_out) + 9) // 10)
        start = page * 10
        slice_out = active_out[start:start + 10]
        
        buttons = []
        for out in slice_out:
            buttons.append([
                Button.inline(
                    f"{out['name']} ({out['amount']:.2f})",
                    f"orp_{debt_type}_{out['id']}"
                )
            ])
        
        # Navigation buttons
        nav_buttons = []
        callback_prefix = "out_irep" if debt_type == "take" else "out_herep"
        if page > 0:
            nav_buttons.append(Button.inline(
                t(user_id, 'previous'),
                f"{callback_prefix}_{page-1}"
            ))
        if page + 1 < total_pages:
            nav_buttons.append(Button.inline(
                t(user_id, 'next'),
                f"{callback_prefix}_{page+1}"
            ))
        if nav_buttons:
            buttons.append(nav_buttons)
        
        # Back button
        buttons.append([
            Button.inline(t(user_id, 'back'), b"out_main")
        ])
        
        await event.edit(
            f"{t(user_id, 'repay_list_work')}\n"
            f"{t(user_id, 'page')}: {page + 1} / {total_pages}",
            buttons=buttons
        )
    
    async def show_out_grid(self, event):
        """
        আউটস্ট্যান্ডিং গ্রিড দেখায় (বামে দিয়েছি, ডানে নিয়েছি)
        """
        user_id = event.sender_id
        from bot.database.repositories import OutstandingRepository
        
        give_list = OutstandingRepository.get_by_type(user_id, "give")
        take_list = OutstandingRepository.get_by_type(user_id, "take")
        
        buttons = []
        max_len = max(len(give_list), len(take_list))
        
        for i in range(max_len):
            row = []
            
            # Left side - Give (দিয়েছি)
            if i < len(give_list):
                d = give_list[i]
                row.append(Button.inline(
                    f"⬆️ {d['name']} {d['amount']:.2f}",
                    f"ovdet_{d['name']}"
                ))
            else:
                row.append(Button.inline("-", b"noop"))
            
            # Right side - Take (নিয়েছি)
            if i < len(take_list):
                d = take_list[i]
                row.append(Button.inline(
                    f"⬇️ {d['name']} {d['amount']:.2f}",
                    f"ovdet_{d['name']}"
                ))
            else:
                row.append(Button.inline("-", b"noop"))
            
            buttons.append(row)
        
        # Back button
        buttons.append([
            Button.inline(t(user_id, 'back'), b"out_main")
        ])
        
        await event.edit(t(user_id, 'out_grid'), buttons=buttons)
    
    async def show_out_person_history(self, event, name):
        """
        আউটস্ট্যান্ডিং এ নির্দিষ্ট ব্যক্তির ইতিহাস দেখায়
        """
        user_id = event.sender_id
        from bot.database.repositories import OutstandingHistoryRepository
        
        history = OutstandingHistoryRepository.get_by_name(user_id, name)
        
        msg = f"{t(user_id, 'out_history', name)}\n"
        msg += "━━━━━━━━━━━━━━━━━━\n"
        
        if not history:
            msg += t(user_id, 'no_transactions')
        else:
            for h in history:
                icon = "💰" if h['amount'] > 0 else "💸"
                msg += f"{icon} {h['amount']:+.2f} | {h['date']} | {h['time']}\n"
        
        buttons = [
            [
                Button.inline(t(user_id, 'back'), b"out_list"),
                Button.inline(t(user_id, 'delete'), f"delout_{name}")
            ]
        ]
        
        await event.edit(msg, buttons=buttons)
    
    async def delete_out_person_data(self, event, name):
        """
        নির্দিষ্ট ব্যক্তির সব আউটস্ট্যান্ডিং ডাটা ডিলিট করে
        """
        user_id = event.sender_id
        from bot.database.repositories import OutstandingRepository, OutstandingHistoryRepository
        
        OutstandingRepository.delete_by_name(user_id, name)
        OutstandingHistoryRepository.delete_by_name(user_id, name)
        
        await event.edit(
            t(user_id, 'out_deleted', name),
            buttons=[Button.inline(t(user_id, 'back'), b"out_list")]
        )
