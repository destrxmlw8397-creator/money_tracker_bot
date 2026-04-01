"""
Goal Handler Module
Handles /goal command for savings goals management
"""

import math
import logging
from telethon import Button
from bot.handlers.base import BaseHandler
from bot.utils.translations import t
from bot.utils.helpers import get_current_date, get_current_time
from bot.database.repositories import GoalRepository, GoalHistoryRepository

logger = logging.getLogger(__name__)


class GoalHandler(BaseHandler):
    """
    Handler for /goal command
    Manages savings goals (add, save, view progress, delete)
    """
    
    async def show_goal_menu(self, event):
        """
        Handle /goal command - show main goal management menu
        This is called when user types /goal (first time)
        """
        user_id = event.sender_id
        
        buttons = [
            [Button.inline(t(user_id, 'goal_list'), b"glist_0")],
            [Button.inline(t(user_id, 'goal_details'), b"gdet_0")],
            [Button.inline(t(user_id, 'cancel'), b"cancel_state")]
        ]
        
        # MongoDB version uses respond for first time command
        await event.respond(t(user_id, 'goal_manager'), buttons=buttons, parse_mode=None)
    
    async def show_goal_menu_callback(self, event):
        """
        Show goal menu when coming back from callback (edit existing message)
        This is called when user clicks back button from within goal menu
        """
        user_id = event.sender_id
        
        buttons = [
            [Button.inline(t(user_id, 'goal_list'), b"glist_0")],
            [Button.inline(t(user_id, 'goal_details'), b"gdet_0")],
            [Button.inline(t(user_id, 'cancel'), b"cancel_state")]
        ]
        
        # MongoDB version uses edit for callback back navigation
        await event.edit(t(user_id, 'goal_manager'), buttons=buttons, parse_mode=None)
    
    async def show_goal_list(self, event, page=0):
        """
        Show list of all goals with saved/target amounts
        This is called from callback when user clicks goal_list button
        """
        user_id = event.sender_id
        rows = GoalRepository.get_all(user_id)
        
        total_pages = max(1, (len(rows) + 9) // 10)
        start = page * 10
        slice_rows = rows[start:start + 10]
        
        buttons = []
        for row in slice_rows:
            buttons.append([
                Button.inline(
                    f"{row['name']} ({row['saved']:.0f}/{row['target']:.0f})",
                    f"gsave_{row['name']}"
                )
            ])
        
        # Navigation buttons
        nav_buttons = []
        if page > 0:
            nav_buttons.append(Button.inline(t(user_id, 'previous'), f"glist_{page-1}"))
        if page + 1 < total_pages:
            nav_buttons.append(Button.inline(t(user_id, 'next'), f"glist_{page+1}"))
        if nav_buttons:
            buttons.append(nav_buttons)
        
        # Add new goal and back buttons
        buttons.append([
            Button.inline(t(user_id, 'add_new_goal'), b"new_goal"),
            Button.inline(t(user_id, 'back'), b"goal_main")
        ])
        
        msg = f"{t(user_id, 'your_goals')}\n{t(user_id, 'page')}: {page + 1} / {total_pages}"
        
        # MongoDB version uses edit for callback
        await event.edit(msg, buttons=buttons, parse_mode=None)
    
    async def show_goal_details_menu(self, event, page=0):
        """
        Show progress percentages for all goals
        This is called from callback when user clicks goal_details button
        """
        user_id = event.sender_id
        rows = GoalRepository.get_all(user_id)
        
        if not rows:
            await event.edit(t(user_id, 'no_goals'), buttons=[[Button.inline(t(user_id, 'back'), b"goal_main")]], parse_mode=None)
            return
        
        buttons = []
        for row in rows:
            percent = (row['saved'] / row['target'] * 100) if row['target'] > 0 else 0
            buttons.append([
                Button.inline(
                    f"🎯 {row['name']} {percent:.0f}%",
                    f"vgoal_{row['name']}"
                )
            ])
        
        buttons.append([
            Button.inline(t(user_id, 'back'), b"goal_main")
        ])
        
        # MongoDB version uses edit for callback
        await event.edit(t(user_id, 'goal_progress'), buttons=buttons, parse_mode=None)
    
    async def show_goal_history(self, event, goal_name):
        """
        Show transaction history for a specific goal
        This is called from callback when user clicks on a goal from details menu
        """
        user_id = event.sender_id
        history = GoalHistoryRepository.get_by_name(user_id, goal_name, limit=10)
        
        msg = f"{t(user_id, 'goal_detail', goal_name)}\n"
        msg += "━━━━━━━━━━━━━━━━━━\n"
        
        if not history:
            msg += t(user_id, 'no_savings')
        else:
            for h in history:
                msg += f"🔹 {h['amount']:+.2f} | {h['date']} | {h['time']}\n"
        
        buttons = [[Button.inline(t(user_id, 'back'), b"gdet_0")]]
        
        # MongoDB version uses edit for callback
        await event.edit(msg, buttons=buttons, parse_mode=None)
    
    async def add_new_goal_prompt(self, event):
        """
        Show prompt to add new goal
        This is called from callback when user clicks add_new_goal button
        """
        user_id = event.sender_id
        
        # Set user state in message handler
        from bot.handlers.message import MessageHandler
        MessageHandler.user_states[event.sender_id] = "ST_NEW_GOAL"
        
        # MongoDB version uses edit for callback
        await event.edit(
            t(user_id, 'enter_goal'),
            buttons=[Button.inline(t(user_id, 'back'), b"goal_main")],
            parse_mode=None
        )
    
    async def add_savings_prompt(self, event, goal_name):
        """
        Show prompt to add savings to a goal
        This is called from callback when user clicks on a goal from goal list
        """
        user_id = event.sender_id
        
        # Set user state in message handler
        from bot.handlers.message import MessageHandler
        MessageHandler.user_states[event.sender_id] = f"ST_SAVE_GOAL_{goal_name}"
        
        buttons = [
            [Button.inline(t(user_id, 'delete_goal_confirm'), f"delgoal_{goal_name}")],
            [Button.inline(t(user_id, 'back'), b"glist_0")]
        ]
        
        # MongoDB version uses edit for callback
        await event.edit(
            t(user_id, 'enter_save_amount', goal_name),
            buttons=buttons,
            parse_mode=None
        )
    
    async def delete_goal_confirm(self, event, goal_name):
        """
        Show confirmation dialog for goal deletion
        This is called from callback when user clicks delete button
        """
        user_id = event.sender_id
        
        buttons = [
            [
                Button.inline(t(user_id, 'confirm'), f"confdelgoal_{goal_name}"),
                Button.inline(t(user_id, 'no'), f"gsave_{goal_name}")
            ]
        ]
        
        # MongoDB version uses edit for callback
        await event.edit(
            t(user_id, 'delete_goal_confirm', goal_name),
            buttons=buttons,
            parse_mode=None
        )
    
    async def execute_delete_goal(self, event, goal_name):
        """
        Execute goal deletion
        This is called from callback when user confirms deletion
        """
        user_id = event.sender_id
        
        GoalRepository.delete_by_name(user_id, goal_name)
        GoalHistoryRepository.delete_by_name(user_id, goal_name)
        
        # MongoDB version uses edit for callback
        await event.edit(
            t(user_id, 'goal_deleted', goal_name),
            buttons=[Button.inline(t(user_id, 'back'), b"glist_0")],
            parse_mode=None
        )
    
    async def execute_add_goal(self, user_id, text):
        """
        Process new goal input
        This is called from message handler when user enters goal details
        """
        try:
            parts = text.split()
            if len(parts) < 2:
                return False, "❌ নাম এবং টার্গেট লিখুন। যেমন: ল্যাপটপ 50000", None
            
            name = parts[0]
            target = float(parts[1])
            
            GoalRepository.add_or_update(user_id, name, target)
            return True, f"✅ লক্ষ্য সেট হয়েছে: {name}", name
            
        except ValueError:
            return False, "❌ টার্গেট সংখ্যা হতে হবে। যেমন: ল্যাপটপ 50000", None
        except Exception as e:
            return False, f"❌ ত্রুটি: {e}", None
    
    async def execute_add_savings(self, user_id, goal_name, amount):
        """
        Process savings addition to goal
        This is called from message handler when user enters savings amount
        """
        try:
            GoalRepository.add_savings(user_id, goal_name, amount)
            GoalHistoryRepository.add(
                user_id, goal_name, amount,
                get_current_date(None), get_current_time(None)
            )
            return True, f"✅ সফলভাবে {amount:.2f} টাকা '{goal_name}' লক্ষ্যে জমা করা হয়েছে।"
        except Exception as e:
            return False, f"❌ ত্রুটি: {e}"
