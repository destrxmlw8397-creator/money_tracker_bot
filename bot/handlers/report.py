from bot.handlers.base import BaseHandler
from bot.utils.translations import t
from bot.utils.helpers import get_current_month, get_current_date
from bot.database.repositories import BalanceRepository
from telethon import Button

class ReportHandler(BaseHandler):
    async def show_report_options(self, event):
        user_id = event.sender_id
        buttons = [
            [Button.inline(t(user_id, 'today_income_expenses'), b"rep_today")],
            [Button.inline(t(user_id, 'date_wise'), b"rep_date")],
            [Button.inline(t(user_id, 'monthly_wise'), b"mrep_0")],
            [Button.inline(t(user_id, 'cancel'), b"cancel_state")]
        ]
        await event.respond(t(user_id, 'select_report'), buttons=buttons)
    
    async def send_monthly_summary_page(self, user_id, chat_id, page_index, message_id=None):
        all_months = BalanceRepository.get_all_months(user_id)
        if not all_months:
            await self.client.send_message(chat_id, t(user_id, 'no_data'))
            return
        
        all_months = all_months[::-1]
        total_months = len(all_months)
        
        if page_index < 0 or page_index >= total_months:
            return
        
        target = all_months[page_index]
        month_key = target.get('month', 'Unknown')
        history = target.get('history', [])
        
        total_inc = target.get('total_income', 0)
        total_exp = target.get('total_expense', 0)
        
        daily_stats = {}
        for entry in history:
            d = entry.get('date', 'Unknown')
            amt = entry.get('amount', 0.0)
            if d not in daily_stats:
                daily_stats[d] = {'inc': 0.0, 'exp': 0.0}
            
            if entry.get("is_debt_logic") and not entry.get("is_outstanding_repay"):
                continue
            
            if amt > 0:
                daily_stats[d]['inc'] += amt
            else:
                daily_stats[d]['exp'] += abs(amt)
        
        msg = f"📅 **{t(user_id, 'monthly_report', month_key)}**\n━━━━━━━━━━━━━━━━━━\n"
        
        for date in sorted(daily_stats.keys(), reverse=True):
            stats = daily_stats[date]
            net = stats['inc'] - stats['exp']
            msg += f"🗓 **{date}**\n"
            msg += f"{t(user_id, 'total_income')}: {stats['inc']:.0f} | {t(user_id, 'total_expense')}: {stats['exp']:.0f} | {t(user_id, 'net')}: {net:.0f}\n"
            msg += "┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n"
        
        msg += f"{t(user_id, 'total_income')}: {total_inc:.2f}\n"
        msg += f"{t(user_id, 'total_expense')}: {total_exp:.2f}\n"
        msg += f"{t(user_id, 'net')}: {total_inc - total_exp:.2f}\n"
        msg += f"{t(user_id, 'page')}: {page_index + 1} / {total_months}"
        
        buttons = []
        nav = []
        if page_index < total_months - 1:
            nav.append(Button.inline(t(user_id, 'previous'), f"mrep_{page_index + 1}"))
        if page_index > 0:
            nav.append(Button.inline(t(user_id, 'next'), f"mrep_{page_index - 1}"))
        if nav:
            buttons.append(nav)
        buttons.append([Button.inline(t(user_id, 'back'), b"rep_main")])
        
        if message_id:
            await self.client.edit_message(chat_id, message_id, msg, buttons=buttons)
        else:
            await self.client.send_message(chat_id, msg, buttons=buttons)
