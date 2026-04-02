"""
Translations Module
Handles multi-language support (Bengali and English)
"""

from bot.database.repositories import UserRepository

# Complete translations dictionary
TRANSLATIONS = {
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
        'welcome': '👤 <b>প্রো মাসিক হিসাব রক্ষক!</b>\n\n📅 বর্তমান মাস: <b>{}</b>\n\n📌 <b>কিভাবে হিসাব লিখবেন?</b>\n• শুধু সংখ্যা: <code>500</code> বা <code>-200</code>\n• ক্যাটাগরিসহ: <code>খাবার -300</code> বা <code>বেতন 20000</code>\n• ওয়ালেটসহ: <code>বিকাশ ২০০ বেতন</code> বা <code>ব্যাংক -৫০০ বিল</code> (ডিফল্ট: Cash)\n\n📌 <b>কমান্ডসমূহ:</b>\n• /balance - বর্তমান রিপোর্ট ও ওয়ালেট\n• /report - আজকের বা তারিখ ভিত্তিক রিপোর্ট\n• /history - বিস্তারিত ইতিহাস (Pagination)\n• /debt - লোন বা ধার ট্র্যাকার\n• /goal - সেভিংস গোল স্ট্যাটাস\n• /trns_money - এক ওয়ালেট থেকে অন্য ওয়ালেটে টাকা স্থানান্তর\n• /pdf - পিডিএফ রিপোর্ট ডাউনলোড\n• /setbudget - বাজেট সেট\n• /addwallet - নতুন ওয়ালেট যোগ করুন\n• /delwallet - ওয়ালেট মুছে ফেলুন\n• /undo - শেষ এন্ট্রি মুছুন\n• /reset - হিসাব মুছুন (উন্নত অপশন)',
        
        # Balance
        'lifetime_report': '🏦 <b>সর্বমোট হিসাব (Life-time Report)</b>',
        'total_income': '💰 মোট জমা',
        'total_expense': '💸 মোট খরচ',
        'total_receivable': '⬆️ মোট পাওনা (লোন)',
        'total_payable': '⬇️ মোট দেনা (ধার)',
        'current_wallet': '🏦 <b>বর্তমান ওয়ালেট ব্যালেন্স:</b>',
        'net_balance': '✅ <b>আপনার হাতে আছে: {} টাকা</b>',
        'no_wallet': 'কোন ওয়ালেট নেই',
        'next_month': 'পরের মাস ➡️',
        'previous_month': '⬅️ আগের মাস',
        'previous_life': '⬅️ আগের (Life)',
        'monthly_report': '📊 <b>মাসিক রিপোর্ট ({})</b>',
        'monthly_receivable': '⬆️ মাসিক পাওনা (লোন)',
        'monthly_payable': '⬇️ মাসিক দেনা (ধার)',
        'remaining': '✅ <b>অবশিষ্ট: {} টাকা</b>',
        'budget_usage': '⚠️ বাজেট ব্যবহার: {:.1f}% ({:.1f}/{:.1f})',
        'wallet_balance': '💳 {}: {:.2f}',
        
        # Report
        'today_report': '📅 <b>আজকের রিপোর্ট ({})</b>',
        'date_report': '📅 <b>রিপোর্ট: {}</b>',
        'net': '⚖️ নীট',
        'select_report': '📊 <b>কোন রিপোর্টটি দেখতে চান?</b>',
        'today_income_expenses': '📅 আজকের আয় ও ব্যয়',
        'date_wise': '🗓 তারিখ অনুযায়ী আয় ও ব্যয়',
        'monthly_wise': '📆 মাসিক আয় ও ব্যয়',
        'enter_date': '📅 নির্দিষ্ট তারিখের রিপোর্ট দেখতে তারিখটি লিখুন।\nউদাহরণ: <code>11-01-2026</code>',
        
        # History
        'detailed_history': '📂 <b>বিস্তারিত ইতিহাস ({})</b>',
        'previous': '⬅️ আগের',
        'next': 'পরের ➡️',
        'no_history': '❌ কোনো তথ্য নেই।',
        
        # PDF
        'pdf_options': '📄 <b>কোন ধরণের পিডিএফ রিপোর্ট চান?</b>',
        'pdf_current': '📊 চলতি মাসের রিপোর্ট',
        'pdf_month_wise': '🗓 মাস ভিত্তিক রিপোর্ট',
        'pdf_today': '📅 আজকের রিপোর্ট',
        'pdf_date_wise': '🔍 তারিখ ভিত্তিক রিপোর্ট',
        'pdf_month_prompt': '📌 নির্দিষ্ট মাসের পিডিএফ পেতে মাস-বছর লিখুন (যেমন: Jan-2026):',
        'pdf_date_prompt': '📌 নির্দিষ্ট তারিখের পিডিএফ পেতে তারিখটি লিখুন (যেমন: 01-01-2026):',
        'pdf_sent': '✅ আপনার {} মাসের পূর্ণাঙ্গ রিপোর্ট।',
        'pdf_today_sent': '✅ আজকের ({}) রিপোর্ট।',
        'pdf_no_data': '❌ আজ কোনো লেনদেন হয়নি।',
        'pdf_no_data_month': '❌ তথ্য পাওয়া যায়নি।',
        
        # Debt
        'debt_manager': '⚖️ <b>লোন ও ধার ম্যানেজার</b>',
        'give': '💸 দিয়েছি',
        'take': '💰 নিয়েছি',
        'i_repaid': '✅ আমি পরিশোধ করেছি',
        'he_repaid': '🤝 সে পরিশোধ করেছে',
        'debt_list': '📋 লিস্ট',
        'outstanding': '💳 আউটস্ট্যান্ডিং',
        'select_person': '👤 {} কার সাথে?',
        'will_receive': 'পাবেন',
        'will_pay': 'দিবেন',
        'enter_amount': '💰 <b>{}</b>-{} কত টাকা?\nশুধুমাত্র সংখ্যাটি লিখুন।',
        'to_give': 'কে দিয়েছেন',
        'to_take': 'কাছ থেকে নিয়েছেন',
        'add_new_person': '👤 নতুন ব্যক্তির নাম ও টাকা লিখুন।\nউদাহরণ: <code>Rahim 500</code>',
        'repay_list': '👤 তালিকা থেকে সিলেক্ট করুন:',
        'no_list': '❌ কোনো লিস্ট পাওয়া যায়নি।',
        'no_list_alert': '❌ কোনো লিস্ট নেই।',
        'debt_grid': '⚖️ <b>পাওনা (বাম) | দেনা (ডান)</b>',
        'person_history': '📂 <b>{} এর সাথে লেনদেন</b>',
        'no_transactions': 'এখনো কোনো লেনদেন হয়নি।',
        'delete_confirm': '⚠️ আপনি কি নিশ্চিত যে <b>{}</b> এর সকল ডাটা মুছে ফেলতে চান?',
        'deleted': '🗑️ <b>{}</b> এর ডাটা সফলভাবে মুছে ফেলা হয়েছে।',
        'updated': '✅ আপডেট হয়েছে: {} {}',
        'new_entry': '✅ নতুন এন্ট্রি: {} {}',
        'repay_success': '✅ পরিশোধ আপডেট! বর্তমান ব্যালেন্স: {}',
        'select_wallet_for_give': '💳 কোন ওয়ালেট থেকে <b>{}</b> টাকা <b>{}</b> কে ধার দিবেন?',
        'select_wallet_for_take': '💳 কোন ওয়ালেটে <b>{}</b> টাকা <b>{}</b> এর কাছ থেকে ধার নিবেন?',
        'select_wallet_for_i_repaid': '💳 কোন ওয়ালেট থেকে <b>{}</b> টাকা <b>{}</b> কে পরিশোধ করবেন?',
        'select_wallet_for_he_repaid': '💳 কোন ওয়ালেটে <b>{}</b> টাকা <b>{}</b> এর কাছ থেকে পরিশোধ নিবেন?',
        'select_wallet_for_out_give': '💳 <b>{}</b> টাকা <b>{}</b> এর কাছ থেকে পাবেন। কোন ওয়ালেটে নিবেন?',
        'select_wallet_for_out_take': '💳 <b>{}</b> টাকা <b>{}</b> কে দিবেন। কোন ওয়ালেট থেকে দিবেন?',
        
        # Outstanding
        'out_manager': '💳 <b>আউটস্ট্যান্ডিং পেমেন্ট ম্যানেজার</b>\n(এন্ট্রি দিলে ব্যালেন্স পরিবর্তন হবে না, কিন্তু রিপে করলে হবে)',
        'give_work': '💸 দিয়েছি (Work)',
        'take_work': '💰 নিয়েছি (Work)',
        'i_repaid_work': '✅ আমি পরিশোধ করেছি (Work)',
        'he_repaid_work': '🤝 সে পরিশোধ করেছে (Work)',
        'debt_list_work': '📋 লিস্ট (Work)',
        'out_grid': '⚖️ <b>আউটস্ট্যান্ডিং: দিয়েছি | নিয়েছি</b>',
        'out_history': '📂 <b>{} (Work) ইতিহাস</b>',
        'out_entry_success': '✅ এন্ট্রি সফল (Work): {} {}\n(ব্যালেন্স পরিবর্তন হয়নি)',
        'out_new_success': '✅ নতুন এন্ট্রি (Work): {} {}\n(ব্যালেন্স পরিবর্তন হয়নি)',
        'out_repay_success': '✅ রিপে সফল! বর্তমান বাকি: {}\n(মেইন ব্যালেন্স ও ওয়ালেট আপডেট করা হয়েছে)',
        'enter_out_amount': '💰 <b>{}</b>-{} কত টাকা?\n(ব্যালেন্স পরিবর্তন হবে না)',
        'select_name_work': '👤 নাম সিলেক্ট করুন (Work):',
        'repay_list_work': '👤 রিপে তালিকা (Work):',
        'delete_out_confirm': '⚠️ আপনি কি নিশ্চিত যে <b>{}</b> এর সকল আউটস্ট্যান্ডিং ডাটা মুছে ফেলতে চান?',
        'out_deleted': '🗑️ <b>{}</b> এর সকল Work ডাটা মুছে ফেলা হয়েছে।',
        
        # Goal
        'goal_manager': '🎯 <b>সেভিংস গোল ম্যানেজার</b>',
        'goal_list': '📋 গোল লিস্ট',
        'goal_details': '📊 গোলের বিবরণ',
        'your_goals': '📋 <b>আপনার সেভিংস গোল সমূহ</b>',
        'goal_progress': '📊 <b>লক্ষ্য অনুযায়ী অগ্রগতি:</b>\nডিটেইলস দেখতে বাটনে ক্লিক করুন।',
        'goal_detail': '📂 <b>গোল ডিটেইলস: {}</b>',
        'no_savings': 'এখনো কোনো টাকা জমা করা হয়নি।',
        'enter_goal': '🎯 নতুন গোলের নাম এবং টার্গেট লিখুন।\nউদাহরণ: <code>ল্যাপটপ ৫০০০০</code>',
        'enter_save_amount': '💰 <b>\'{}\'</b> গোলে কত টাকা জমা করতে চান?\nশুধুমাত্র সংখ্যাটি লিখুন।',
        'goal_set': '✅ লক্ষ্য সেট হয়েছে: {}',
        'goal_saved': '✅ সফলভাবে <b>{}</b> টাকা <b>\'{}\'</b> লক্ষ্যে জমা করা হয়েছে।',
        'delete_goal_confirm': '⚠️ আপনি কি নিশ্চিত যে <b>\'{}\'</b> গোলটি ডিলিট করতে চান?',
        'goal_deleted': '🗑️ গোল <b>\'{}\'</b> ডিলিট করা হয়েছে।',
        'add_new_goal': '➕ নতুন গোল',
        
        # Transfer
        'transfer_from': '💳 <b>কোন ওয়ালেট থেকে ট্রান্সফার করতে চান?</b>',
        'transfer_to': '💳 <b>উৎস: {}</b>\n\n📥 <b>কোন ওয়ালেটে পাঠাবেন?</b>',
        'enter_transfer_amount': '💰 কত টাকা <b>{}</b> থেকে <b>{}</b> এ ট্রান্সফার করতে চান?\nশুধুমাত্র সংখ্যাটি লিখুন।',
        'transfer_success': '✅ সফলভাবে <b>{}</b> টাকা <b>{}</b> থেকে <b>{}</b> এ স্থানান্তরিত হয়েছে।',
        'insufficient_balance': '❌ পর্যাপ্ত ব্যালেন্স নেই! <b>{}</b> এ উপলব্ধ: <b>{:.2f}</b> টাকা, প্রয়োজন: <b>{:.2f}</b> টাকা',
        'back_to_from': '🔙 পেছনে ফিরুন',
        'lifetime_balance_info': 'ℹ️ <b>লাইফটাইম ব্যালেন্স</b>: {:.2f} টাকা',
        
        # Wallet
        'select_wallet_delete': '💳 <b>ডিলিট করার জন্য ওয়ালেট সিলেক্ট করুন:</b>',
        'delete_wallet_confirm': '⚠️ আপনি কি নিশ্চিত যে আপনি <b>\'{}\'</b> ওয়ালেটটি ডিলিট করতে চান? (ব্যালেন্স হারাবে)',
        'wallet_deleted': '🗑️ ওয়ালেট <b>\'{}\'</b> সফলভাবে ডিলিট করা হয়েছে।',
        'wallet_exists': '❌ ওয়ালেট \'{}\' আগে থেকেই আছে।',
        'wallet_added': '✅ নতুন ওয়ালেট \'{}\' যোগ করা হয়েছে।',
        'enter_wallet_name': '💳 নতুন ওয়ালেটের নাম লিখুন (যেমন: Rocket বা Nagad)।',
        
        # Budget
        'enter_budget': '💰 আপনার বাজেট কত তা লিখুন।',
        'budget_set': '✅ বাজেট {} সেট হয়েছে।',
        
        # Reset
        'reset_confirm': '⚠️ সব ডাটা মুছে ফেলতে চান?',
        'reset_month_confirm': '⚠️ আপনি কি নিশ্চিত যে <b>{}</b> মাসের সব হিসাব মুছে ফেলবেন?',
        'reset_month_success': '✅ <b>{}</b> মাসের সব হিসাব সফলভাবে মুছে ফেলা হয়েছে!',
        'reset_all_success': '🗑️ সব ডাটা মুছে ফেলা হয়েছে।',
        
        # Entry
        'entry_success': '✅ {}: <b>{}</b>\n📂 খাত: <b>{}</b>\n💳 ওয়ালেট: <b>{}</b>',
        'deposit': '💰 জমা',
        'expense': '💸 খরচ',
        'undo_success': '🗑 শেষ এন্ট্রি ({}) মোছা হয়েছে।',
        
        # Language
        'select_language': '🌐 <b>আপনার ভাষা নির্বাচন করুন:</b>',
        'language_set': '✅ ভাষা সেট করা হয়েছে: বাংলা',
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
        'welcome': '👤 <b>Pro Monthly Account Keeper!</b>\n\n📅 Current month: <b>{}</b>\n\n📌 <b>How to add entries?</b>\n• Just number: <code>500</code> or <code>-200</code>\n• With category: <code>Food -300</code> or <code>Salary 20000</code>\n• With wallet: <code>bkash 200 salary</code> or <code>bank -500 bill</code> (Default: Cash)\n\n📌 <b>Commands:</b>\n• /balance - Current report & wallet\n• /report - Today or date wise report\n• /history - Detailed history (Pagination)\n• /debt - Loan tracker\n• /goal - Savings goal status\n• /trns_money - Transfer money between wallets\n• /pdf - Download PDF report\n• /setbudget - Set budget\n• /addwallet - Add new wallet\n• /delwallet - Delete wallet\n• /undo - Delete last entry\n• /reset - Delete all data (advanced)',
        
        # Balance
        'lifetime_report': '🏦 <b>Lifetime Report</b>',
        'total_income': '💰 Total Income',
        'total_expense': '💸 Total Expense',
        'total_receivable': '⬆️ Total Receivable (Loan)',
        'total_payable': '⬇️ Total Payable (Debt)',
        'current_wallet': '🏦 <b>Current Wallet Balance:</b>',
        'net_balance': '✅ <b>You have: {} Taka</b>',
        'no_wallet': 'No wallets',
        'next_month': 'Next Month ➡️',
        'previous_month': '⬅️ Previous Month',
        'previous_life': '⬅️ Previous (Life)',
        'monthly_report': '📊 <b>Monthly Report ({})</b>',
        'monthly_receivable': '⬆️ Monthly Receivable',
        'monthly_payable': '⬇️ Monthly Payable',
        'remaining': '✅ <b>Remaining: {} Taka</b>',
        'budget_usage': '⚠️ Budget Usage: {:.1f}% ({:.1f}/{:.1f})',
        'wallet_balance': '💳 {}: {:.2f}',
        
        # Report
        'today_report': '📅 <b>Today\'s Report ({})</b>',
        'date_report': '📅 <b>Report: {}</b>',
        'net': '⚖️ Net',
        'select_report': '📊 <b>Which report do you want to see?</b>',
        'today_income_expenses': '📅 Today\'s Income & Expenses',
        'date_wise': '🗓 Date Wise Income & Expenses',
        'monthly_wise': '📆 Monthly Wise Income & Expenses',
        'enter_date': '📅 Enter date to see report.\nExample: <code>11-01-2026</code>',
        
        # History
        'detailed_history': '📂 <b>Detailed History ({})</b>',
        'previous': '⬅️ Previous',
        'next': 'Next ➡️',
        'no_history': '❌ No history found.',
        
        # PDF
        'pdf_options': '📄 <b>Which PDF report do you want?</b>',
        'pdf_current': '📊 Current Month Report',
        'pdf_month_wise': '🗓 Month Wise Report',
        'pdf_today': '📅 Today\'s Report',
        'pdf_date_wise': '🔍 Date Wise Report',
        'pdf_month_prompt': '📌 Enter month-year for PDF (e.g., Jan-2026):',
        'pdf_date_prompt': '📌 Enter date for PDF (e.g., 01-01-2026):',
        'pdf_sent': '✅ Your complete report for {}.',
        'pdf_today_sent': '✅ Today\'s ({}) report.',
        'pdf_no_data': '❌ No transactions today.',
        'pdf_no_data_month': '❌ No data found.',
        
        # Debt
        'debt_manager': '⚖️ <b>Loan & Debt Manager</b>',
        'give': '💸 Give',
        'take': '💰 Take',
        'i_repaid': '✅ I repaid',
        'he_repaid': '🤝 He/She repaid',
        'debt_list': '📋 Debt list',
        'outstanding': '💳 Outstanding Payment',
        'select_person': '👤 {} person?',
        'will_receive': 'Receive from',
        'will_pay': 'Pay to',
        'enter_amount': '💰 Enter amount for <b>{}</b>-{}?\nJust the number.',
        'to_give': 'gave to',
        'to_take': 'took from',
        'add_new_person': '👤 Enter new person name and amount.\nExample: <code>Rahim 500</code>',
        'repay_list': '👤 Select from list:',
        'no_list': '❌ No list found.',
        'no_list_alert': '❌ No list available.',
        'debt_grid': '⚖️ <b>Receivable (Left) | Payable (Right)</b>',
        'person_history': '📂 <b>Transactions with {}</b>',
        'no_transactions': 'No transactions yet.',
        'delete_confirm': '⚠️ Are you sure you want to delete all data of <b>{}</b>?',
        'deleted': '🗑️ <b>{}</b>\'s data deleted successfully.',
        'updated': '✅ Updated: {} {}',
        'new_entry': '✅ New entry: {} {}',
        'repay_success': '✅ Repayment updated! Current balance: {}',
        'select_wallet_for_give': '💳 Select wallet to give <b>{}</b> to <b>{}</b>?',
        'select_wallet_for_take': '💳 Select wallet to take <b>{}</b> from <b>{}</b>?',
        'select_wallet_for_i_repaid': '💳 Select wallet to repay <b>{}</b> to <b>{}</b>?',
        'select_wallet_for_he_repaid': '💳 Select wallet to receive <b>{}</b> from <b>{}</b>?',
        'select_wallet_for_out_give': '💳 You will receive <b>{}</b> Taka from <b>{}</b>. Which wallet to receive?',
        'select_wallet_for_out_take': '💳 You will pay <b>{}</b> Taka to <b>{}</b>. Which wallet to pay from?',
        
        # Outstanding
        'out_manager': '💳 <b>Outstanding Payment Management</b>\n(Entry won\'t change balance, but repayment will)',
        'give_work': '💸 Give Work',
        'take_work': '💰 Take Work',
        'i_repaid_work': '✅ I repaid Work',
        'he_repaid_work': '🤝 He repaid Work',
        'debt_list_work': '📋 Debt List Work',
        'out_grid': '⚖️ <b>Outstanding: Give | Take</b>',
        'out_history': '📂 <b>{} (Work) History</b>',
        'out_entry_success': '✅ Entry successful (Work): {} {}\n(Balance unchanged)',
        'out_new_success': '✅ New entry (Work): {} {}\n(Balance unchanged)',
        'out_repay_success': '✅ Repayment successful! Remaining: {}\n(Main balance updated)',
        'enter_out_amount': '💰 Enter amount for <b>{}</b>-{}\n(Balance unchanged)',
        'select_name_work': '👤 Select name (Work):',
        'repay_list_work': '👤 Repayment list (Work):',
        'delete_out_confirm': '⚠️ Are you sure you want to delete all Outstanding data of <b>{}</b>?',
        'out_deleted': '🗑️ All Work data of <b>{}</b> deleted.',
        
        # Goal
        'goal_manager': '🎯 <b>Savings Goal Manager</b>',
        'goal_list': '📋 Goal List',
        'goal_details': '📊 Details Of Goal\'s',
        'your_goals': '📋 <b>Your Savings Goals</b>',
        'goal_progress': '📊 <b>Progress by Goal:</b>\nClick button for details.',
        'goal_detail': '📂 <b>Goal Details: {}</b>',
        'no_savings': 'No savings yet.',
        'enter_goal': '🎯 Enter goal name and target.\nExample: <code>Laptop 50000</code>',
        'enter_save_amount': '💰 How much to save in <b>\'{}\'</b>?\nJust the number.',
        'goal_set': '✅ Goal set: {}',
        'goal_saved': '✅ Successfully saved <b>{}</b> to <b>\'{}\'</b> goal.',
        'delete_goal_confirm': '⚠️ Are you sure you want to delete <b>\'{}\'</b> goal?',
        'goal_deleted': '🗑️ Goal <b>\'{}\'</b> deleted.',
        'add_new_goal': '➕ Add New',
        
        # Transfer
        'transfer_from': '💳 <b>Select wallet to transfer from?</b>',
        'transfer_to': '💳 <b>Source: {}</b>\n\n📥 <b>Select wallet to send to?</b>',
        'enter_transfer_amount': '💰 How much to transfer from <b>{}</b> to <b>{}</b>?\nJust the number.',
        'transfer_success': '✅ Successfully transferred <b>{}</b> from <b>{}</b> to <b>{}</b>.',
        'insufficient_balance': '❌ Insufficient balance! Available in <b>{}</b>: <b>{:.2f}</b>, Required: <b>{:.2f}</b>',
        'back_to_from': '🔙 Back to from',
        'lifetime_balance_info': 'ℹ️ <b>Lifetime Balance</b>: {:.2f}',
        
        # Wallet
        'select_wallet_delete': '💳 <b>Select wallet to delete:</b>',
        'delete_wallet_confirm': '⚠️ Are you sure you want to delete <b>\'{}\'</b> wallet? (Balance will be lost)',
        'wallet_deleted': '🗑️ Wallet <b>\'{}\'</b> deleted successfully.',
        'wallet_exists': '❌ Wallet \'{}\' already exists.',
        'wallet_added': '✅ New wallet \'{}\' added.',
        'enter_wallet_name': '💳 Enter new wallet name (e.g., Rocket or Nagad).',
        
        # Budget
        'enter_budget': '💰 Enter your budget amount.',
        'budget_set': '✅ Budget set to {}.',
        
        # Reset
        'reset_confirm': '⚠️ Delete all data?',
        'reset_month_confirm': '⚠️ Are you sure you want to delete all data for <b>{}</b> month?',
        'reset_month_success': '✅ All data for <b>{}</b> month deleted successfully!',
        'reset_all_success': '🗑️ All data deleted.',
        
        # Entry
        'entry_success': '✅ {}: <b>{}</b>\n📂 Category: <b>{}</b>\n💳 Wallet: <b>{}</b>',
        'deposit': '💰 Deposit',
        'expense': '💸 Expense',
        'undo_success': '🗑 Last entry ({}) deleted.',
        
        # Language
        'select_language': '🌐 <b>Select your language:</b>',
        'language_set': '✅ Language set: English',
        'lang_bn': '🇧🇩 বাংলা',
        'lang_en': '🇬🇧 English'
    }
}

_user_repo = UserRepository()


def get_user_lang(user_id):
    """
    Get user language preference
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        str: 'bn' or 'en'
    """
    return _user_repo.get_language(user_id)


def set_user_lang(user_id, lang):
    """
    Set user language preference
    
    Args:
        user_id: Telegram user ID
        lang: 'bn' or 'en'
    """
    _user_repo.set_language(user_id, lang)


def t(user_id, key, *args):
    """
    Get translated text for a user
    
    Args:
        user_id: Telegram user ID
        key: Translation key
        *args: Format arguments
        
    Returns:
        str: Translated and formatted text
    """
    lang = get_user_lang(user_id)
    text = TRANSLATIONS.get(lang, TRANSLATIONS['bn']).get(key, key)
    if args:
        return text.format(*args)
    return text
