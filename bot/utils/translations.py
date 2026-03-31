from bot.database.repositories import UserRepository
from typing import Dict, Any

# Translations dictionary
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    'bn': {
        # General
        'back': '🔙 ব্যাক',
        'cancel': '❌ ক্যান্সেল',
        'yes': '✅ হ্যাঁ',
        'no': '❌ না',
        'confirm': '✅ হ্যাঁ, নিশ্চিত',
        'delete': '🗑️ ডিলিট',
        'page': '📄 পৃষ্ঠা',
        'main_menu': '🔙 মেইন মেনু',
        'no_data': '❌ কোনো তথ্য পাওয়া যায়নি।',
        'operation_cancelled': '❌ অপারেশন বাতিল করা হয়েছে।',
        'invalid_input': '❌ ইনপুট ভুল। আবার চেষ্টা করুন।',
        'select_option': 'নিচের বাটন থেকে অপশন সিলেক্ট করুন:',
        
        # Start command
        'welcome': '👤 **প্রো মাসিক হিসাব রক্ষক!**\n\n📅 বর্তমান মাস: **{}**\n\n📌 **কিভাবে হিসাব লিখবেন?**\n• শুধু সংখ্যা: `500` বা `-200`\n• ক্যাটাগরিসহ: `খাবার -300` বা `বেতন 20000`\n• ওয়ালেটসহ: `বিকাশ ২০০ বেতন` বা `ব্যাংক -৫০০ বিল` (ডিফল্ট: Cash)\n\n📌 **কমান্ডসমূহ:**\n• /balance - বর্তমান রিপোর্ট ও ওয়ালেট\n• /report - আজকের বা তারিখ ভিত্তিক রিপোর্ট\n• /history - বিস্তারিত ইতিহাস\n• /debt - লোন বা ধার ট্র্যাকার\n• /goal - সেভিংস গোল স্ট্যাটাস\n• /trns_money - টাকা স্থানান্তর\n• /pdf - পিডিএফ রিপোর্ট\n• /setbudget - বাজেট সেট\n• /addwallet - ওয়ালেট যোগ\n• /delwallet - ওয়ালেট মুছুন\n• /undo - শেষ এন্ট্রি মুছুন\n• /reset - হিসাব মুছুন',
        
        # Balance
        'lifetime_report': '🏦 **সর্বমোট হিসাব**',
        'total_income': '💰 মোট জমা',
        'total_expense': '💸 মোট খরচ',
        'total_receivable': '⬆️ মোট পাওনা',
        'total_payable': '⬇️ মোট দেনা',
        'current_wallet': '🏦 **বর্তমান ওয়ালেট ব্যালেন্স:**',
        'net_balance': '✅ **আপনার হাতে আছে: {} টাকা**',
        'no_wallet': 'কোন ওয়ালেট নেই',
        'next_month': 'পরের মাস ➡️',
        'previous_month': '⬅️ আগের মাস',
        'previous_life': '⬅️ আগের (Life)',
        'monthly_report': '📊 **মাসিক রিপোর্ট ({})**',
        'monthly_receivable': '⬆️ মাসিক পাওনা',
        'monthly_payable': '⬇️ মাসিক দেনা',
        'remaining': '✅ **অবশিষ্ট: {} টাকা**',
        'budget_usage': '⚠️ বাজেট ব্যবহার: {:.1f}% ({:.1f}/{:.1f})',
        'wallet_balance': '💳 {}: {:.2f}',
        
        # More translations...
        # (Include all other translations from your original code)
        
        # Language
        'select_language': '🌐 **ভাষা নির্বাচন:**',
        'language_set': '✅ ভাষা সেট: বাংলা',
        'lang_bn': '🇧🇩 বাংলা',
        'lang_en': '🇬🇧 English'
    },
    'en': {
        # General
        'back': '🔙 Back',
        'cancel': '❌ Cancel',
        'yes': '✅ Yes',
        'no': '❌ No',
        'confirm': '✅ Yes, Confirm',
        'delete': '🗑️ Delete',
        'page': '📄 Page',
        'main_menu': '🔙 Main Menu',
        'no_data': '❌ No data found.',
        'operation_cancelled': '❌ Operation cancelled.',
        'invalid_input': '❌ Invalid input. Try again.',
        'select_option': 'Select an option from below:',
        
        # Start command
        'welcome': '👤 **Pro Monthly Account Keeper!**\n\n📅 Current month: **{}**\n\n📌 **How to add entries?**\n• Just number: `500` or `-200`\n• With category: `Food -300` or `Salary 20000`\n• With wallet: `bkash 200 salary` or `bank -500 bill` (Default: Cash)\n\n📌 **Commands:**\n• /balance - Current report & wallet\n• /report - Today or date wise report\n• /history - Detailed history\n• /debt - Loan tracker\n• /goal - Savings goal status\n• /trns_money - Transfer money\n• /pdf - Download PDF report\n• /setbudget - Set budget\n• /addwallet - Add wallet\n• /delwallet - Delete wallet\n• /undo - Delete last entry\n• /reset - Delete all data',
        
        # Balance
        'lifetime_report': '🏦 **Lifetime Report**',
        'total_income': '💰 Total Income',
        'total_expense': '💸 Total Expense',
        'total_receivable': '⬆️ Total Receivable',
        'total_payable': '⬇️ Total Payable',
        'current_wallet': '🏦 **Current Wallet Balance:**',
        'net_balance': '✅ **You have: {} Taka**',
        'no_wallet': 'No wallets',
        'next_month': 'Next Month ➡️',
        'previous_month': '⬅️ Previous Month',
        'previous_life': '⬅️ Previous (Life)',
        'monthly_report': '📊 **Monthly Report ({})**',
        'monthly_receivable': '⬆️ Monthly Receivable',
        'monthly_payable': '⬇️ Monthly Payable',
        'remaining': '✅ **Remaining: {} Taka**',
        'budget_usage': '⚠️ Budget Usage: {:.1f}% ({:.1f}/{:.1f})',
        'wallet_balance': '💳 {}: {:.2f}',
        
        # Language
        'select_language': '🌐 **Select language:**',
        'language_set': '✅ Language set: English',
        'lang_bn': '🇧🇩 বাংলা',
        'lang_en': '🇬🇧 English'
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
