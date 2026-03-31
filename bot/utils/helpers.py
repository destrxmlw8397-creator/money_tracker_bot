from datetime import datetime
from bot.config import Config
import re
from typing import Dict, Any

def get_current_month() -> str:
    """Get current month in format Jan-2026"""
    return datetime.now().strftime("%b-%Y")

def get_current_date() -> str:
    """Get current date in format dd-mm-yyyy"""
    return datetime.now().strftime("%d-%m-%Y")

def get_current_time() -> str:
    """Get current time in format HH:MM"""
    return datetime.now().strftime("%H:%M")

def get_lifetime_wallet_balance(user_id: int, wallet_name: str) -> float:
    """Get lifetime balance for a specific wallet"""
    from bot.database.repositories import BalanceRepository
    
    all_months = BalanceRepository.get_all_months(user_id)
    total_balance = 0.0
    for month_data in all_months:
        total_balance += month_data['wallets'].get(wallet_name, 0.0)
    return total_balance

def parse_entry_text(text: str, available_wallets: Dict[str, float]) -> tuple:
    """Parse user input to extract amount, category, and wallet"""
    wallet = "Cash"
    
    # Find wallet in text
    for w in available_wallets.keys():
        if w.lower() in text.lower():
            wallet = w
            break
    
    # Find amount
    match = re.search(r'([-+]?\d*\.?\d+)', text)
    if not match:
        return None, None, None
    
    amount = float(match.group(1))
    
    # Extract category
    pattern = '|'.join(map(re.escape, available_wallets.keys()))
    category = re.sub(pattern, '', text, flags=re.I)
    category = re.sub(r'[-+]?\d*\.?\d+', '', category).strip() or "General"
    
    return amount, category, wallet
