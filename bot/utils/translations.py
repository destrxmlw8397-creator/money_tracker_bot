from bot.database.repositories import UserRepository
from typing import Dict, Any

# Complete translations from your MongoDB file
# (All 1800+ lines of translations go here)
# I'm including the key structure, but you can copy the full translations
# from your original moneytrckmongoDBatlas.py file

TRANSLATIONS = {
    'bn': {
        'back': '🔙 ব্যাক',
        'cancel': '❌ ক্যান্সেল',
        'yes': '✅ হ্যাঁ',
        'no': '❌ না',
        # ... all your Bengali translations
    },
    'en': {
        'back': '🔙 Back',
        'cancel': '❌ Cancel',
        'yes': '✅ Yes',
        'no': '❌ No',
        # ... all your English translations
    }
}

user_repo = UserRepository()

def get_user_lang(user_id: int) -> str:
    """Get user language"""
    return user_repo.get_language(user_id)

def set_user_lang(user_id: int, lang: str):
    """Set user language"""
    user_repo.set_language(user_id, lang)

def t(user_id: int, key: str, *args) -> str:
    """Get translated text"""
    lang = get_user_lang(user_id)
    text = TRANSLATIONS.get(lang, TRANSLATIONS['bn']).get(key, key)
    if args:
        return text.format(*args)
    return text
