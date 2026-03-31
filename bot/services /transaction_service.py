import os
import json
from datetime import datetime
from fpdf import FPDF
from bot.database.repositories import (
    BalanceRepository, DebtRepository, DebtHistoryRepository
)
from bot.utils.helpers import get_current_month, get_current_date, get_current_time, get_user_now
from bot.utils.temp_storage import store_temp_data
from telethon import Button

# Global user_states for PDF handler (to be moved to appropriate module)
user_states = {}

def get_user_monthly_data(user_id, month_key):
    return BalanceRepository.get_monthly_data(user_id, month_key)

def update_user_db(user_id, amount, category="General", wallet_name="Cash", event=None):
    user_time = get_user_now(event)
    month_key = user_time.strftime("%b-%Y")
    now_date = user_time.strftime("%d-%m-%Y")
    now_time = user_time.strftime("%H:%M")
    
    data = get_user_monthly_data(user_id, month_key)
    entry = {"amount": amount, "category": category, "wallet": wallet_name, "date": now_date, "time": now_time}
    
    data['history'].append(entry)
    data['wallets'][wallet_name] = data['wallets'].get(wallet_name, 0.0) + amount
    
    inc_income = amount if amount > 0 else 0
    inc_expense = abs(amount) if amount < 0 else 0
    
    data['total_income'] += inc_income
    data['total_expense'] += inc_expense
    
    BalanceRepository.update_monthly_data(user_id, month_key, data)

def update_wallet_only(user_id, amount, category, wallet_name, event=None):
    user_time = get_user_now(event)
    month_key = user_time.strftime("%b-%Y")
    now_date = user_time.strftime("%d-%m-%Y")
    now_time = user_time.strftime("%H:%M")
    
    data = get_user_monthly_data(user_id, month_key)
    entry = {"amount": amount, "category": category, "wallet": wallet_name, "date": now_date, "time": now_time, "is_debt_logic": True}
    
    data['history'].append(entry)
    data['wallets'][wallet_name] = data['wallets'].get(wallet_name, 0.0) + amount
    
    BalanceRepository.update_monthly_data(user_id, month_key, data)

def get_lifetime_wallet_balance(user_id, wallet_name):
    all_months = BalanceRepository.get_all_months(user_id)
    total = 0.0
    for month in all_months:
        total += month['wallets'].get(wallet_name, 0.0)
    return total

def generate_pdf(user_id, month_key, history_filter=None, title_suffix=""):
    data = get_user_monthly_data(user_id, month_key)
    if not data or not data.get('history'):
        return None

    history = data['history']
    if history_filter:
        history = [e for e in history if e.get('date') == history_filter]
    
    if not history:
        return None

    total_deposit = total_expenses = total_loan_from = total_loan_to = total_pay_from_tlt = total_pay_to_tlf = 0.0

    for e in history:
        amt = e.get('amount', 0.0)
        is_debt = e.get("is_debt_logic", False)
        is_out_rep = e.get("is_outstanding_repay", False)
        cat = str(e.get('category', ''))
        
        if not is_debt or is_out_rep:
            if amt > 0:
                total_deposit += amt
            else:
                total_expenses += abs(amt)
        else:
            if "Repayment" in cat:
                if amt > 0:
                    total_pay_to_tlf += amt
                else:
                    total_pay_from_tlt += abs(amt)
            else:
                if amt > 0:
                    total_loan_from += amt
                else:
                    total_loan_to += abs(amt)

    net_balance = (total_deposit + total_loan_from + total_pay_to_tlf) - (total_expenses + total_loan_to + total_pay_from_tlt)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(190, 10, txt=f"Money Report - {title_suffix or month_key}", ln=True, align='C')
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 7)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(27, 10, "Total Deposit", 1, 0, 'C', True)
    pdf.cell(27, 10, "Total Expenses", 1, 0, 'C', True)
    pdf.cell(27, 10, "Total Loan From", 1, 0, 'C', True)
    pdf.cell(27, 10, "Total Loan To", 1, 0, 'C', True)
    pdf.cell(28, 10, "Pay To TLF", 1, 0, 'C', True)
    pdf.cell(28, 10, "Pay From TLT", 1, 0, 'C', True)
    pdf.cell(26, 10, "Net Balance", 1, 1, 'C', True)
    
    pdf.set_font("Arial", '', 8)
    pdf.cell(27, 10, f"{total_deposit:.2f}", 1, 0, 'C')
    pdf.cell(27, 10, f"{total_expenses:.2f}", 1, 0, 'C')
    pdf.cell(27, 10, f"{total_loan_from:.2f}", 1, 0, 'C')
    pdf.cell(27, 10, f"{total_loan_to:.2f}", 1, 0, 'C')
    pdf.cell(28, 10, f"{total_pay_from_tlt:.2f}", 1, 0, 'C')
    pdf.cell(28, 10, f"{total_pay_to_tlf:.2f}", 1, 0, 'C')
    
    pdf.set_font("Arial", 'B', 8)
    pdf.cell(26, 10, f"{net_balance:.2f}", 1, 1, 'C')
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 10)
    pdf.set_fill_color(50, 50, 50)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(30, 10, "Date", 1, 0, 'C', True)
    pdf.cell(70, 10, "Category", 1, 0, 'C', True)
    pdf.cell(30, 10, "Wallet", 1, 0, 'C', True)
    pdf.cell(30, 10, "Amount", 1, 0, 'C', True)
    pdf.cell(30, 10, "Time", 1, 1, 'C', True)
    
    pdf.set_font("Arial", size=9)
    pdf.set_text_color(0, 0, 0)
    
    for entry in history:
        if pdf.get_y() > 260:
            pdf.add_page()
        pdf.cell(30, 9, str(entry.get('date', '')), 1, 0, 'C')
        cat = str(entry.get('category', 'General'))
        cat_clean = cat.encode('ascii', 'ignore').decode('ascii')
        pdf.cell(70, 9, (cat_clean[:35] + '..') if len(cat_clean) > 35 else cat_clean, 1, 0, 'L')
        pdf.cell(30, 9, str(entry.get('wallet', 'Cash')), 1, 0, 'C')
        amt = entry.get('amount', 0)
        pdf.cell(30, 9, f"{amt:+.2f}", 1, 0, 'R')
        pdf.cell(30, 9, str(entry.get('time', '')), 1, 1, 'C')
    
    file_name = f"Report_{user_id}_{datetime.now().timestamp()}.pdf"
    pdf.output(file_name)
    return file_name

def process_debt_entry_with_balance(uid, name, amt, dtype, wallet="Cash", event=None):
    user_time = get_user_now(event)
    DebtRepository.add_or_update(uid, name, dtype, amt)
    DebtHistoryRepository.add(
        uid, name, amt,
        user_time.strftime("%d-%m-%Y"),
        user_time.strftime("%I:%M %p")
    )
    if dtype == "give":
        update_wallet_only(uid, -amt, f"Loan to {name}", wallet, event=event)
    elif dtype == "take":
        update_wallet_only(uid, amt, f"Loan from {name}", wallet, event=event)

def process_debt_repayment(uid, d_id, amt, wallet="Cash", event=None):
    user_time = get_user_now(event)
    debt = DebtRepository.get_by_id(d_id)
    if debt:
        new_bal = max(0, debt['amount'] - amt)
        DebtRepository.update_amount(d_id, new_bal)
        DebtHistoryRepository.add(
            uid, debt['name'], -amt,
            user_time.strftime("%d-%m-%Y"),
            user_time.strftime("%I:%M %p")
        )
        if debt['type'] == "give":
            update_wallet_only(uid, amt, f"Repayment from {debt['name']}", wallet, event=event)
        else:
            update_wallet_only(uid, -amt, f"Repayment to {debt['name']}", wallet, event=event)
        return new_bal
    return 0

# Wallet selection functions
async def show_wallets_for_debt(event, user_id, action_type, name, amount, return_callback):
    from bot.utils.translations import t
    month_key = get_current_month(event)
    data = get_user_monthly_data(user_id, month_key)
    wallets = data.get('wallets', {})
    
    if not wallets:
        await event.respond(t(user_id, 'no_wallet'))
        return
    
    if action_type == "give":
        msg = t(user_id, 'select_wallet_for_give', amount, name)
    elif action_type == "take":
        msg = t(user_id, 'select_wallet_for_take', amount, name)
    elif action_type == "i_repaid":
        msg = t(user_id, 'select_wallet_for_i_repaid', amount, name)
    elif action_type == "he_repaid":
        msg = t(user_id, 'select_wallet_for_he_repaid', amount, name)
    else:
        msg = t(user_id, 'select_option')
    
    buttons = []
    for wallet_name, balance in wallets.items():
        temp_data = {
            'type': 'debt_wallet',
            'action': action_type,
            'name': name,
            'amount': amount,
            'wallet': wallet_name
        }
        temp_id = store_temp_data(temp_data)
        callback_data = f"tmp_{temp_id}"
        buttons.append([Button.inline(f"{wallet_name} ({balance:.2f})", callback_data)])
    
    buttons.append([Button.inline(t(user_id, 'cancel'), return_callback)])
    await event.respond(msg, buttons=buttons)

async def show_wallets_for_repayment(event, user_id, action_type, name, amount, debt_id, return_callback):
    from bot.utils.translations import t
    month_key = get_current_month(event)
    data = get_user_monthly_data(user_id, month_key)
    wallets = data.get('wallets', {})
    
    if not wallets:
        await event.respond(t(user_id, 'no_wallet'))
        return
    
    if action_type == "i_repaid":
        msg = t(user_id, 'select_wallet_for_i_repaid', amount, name)
    else:
        msg = t(user_id, 'select_wallet_for_he_repaid', amount, name)
    
    buttons = []
    for wallet_name, balance in wallets.items():
        temp_data = {
            'type': 'repay_wallet',
            'action': action_type,
            'name': name,
            'amount': amount,
            'debt_id': debt_id,
            'wallet': wallet_name
        }
        temp_id = store_temp_data(temp_data)
        callback_data = f"tmp_{temp_id}"
        buttons.append([Button.inline(f"{wallet_name} ({balance:.2f})", callback_data)])
    
    buttons.append([Button.inline(t(user_id, 'cancel'), return_callback)])
    await event.respond(msg, buttons=buttons)

async def show_wallets_for_out_repayment(event, user_id, debt_type, name, amount, debt_id, return_callback):
    from bot.utils.translations import t
    month_key = get_current_month(event)
    data = get_user_monthly_data(user_id, month_key)
    wallets = data.get('wallets', {})
    
    if not wallets:
        await event.respond(t(user_id, 'no_wallet'))
        return
    
    if debt_type == "give":
        msg = t(user_id, 'select_wallet_for_out_give', amount, name)
    else:
        msg = t(user_id, 'select_wallet_for_out_take', amount, name)
    
    buttons = []
    for wallet_name, balance in wallets.items():
        temp_data = {
            'type': 'out_repay_wallet',
            'debt_type': debt_type,
            'name': name,
            'amount': amount,
            'debt_id': debt_id,
            'wallet': wallet_name
        }
        temp_id = store_temp_data(temp_data)
        callback_data = f"tmp_{temp_id}"
        buttons.append([Button.inline(f"{wallet_name} ({balance:.2f})", callback_data)])
    
    buttons.append([Button.inline(t(user_id, 'cancel'), return_callback)])
    await event.respond(msg, buttons=buttons)
