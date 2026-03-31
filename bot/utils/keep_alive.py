# bot/utils/keep_alive.py
import threading
import requests
import time
import os

def keep_alive():
    """Keep the bot alive by pinging every 10 minutes"""
    url = os.environ.get('RENDER_EXTERNAL_URL', 'https://your-bot.onrender.com')
    
    while True:
        try:
            response = requests.get(url, timeout=10)
            print(f"Keep alive ping: {response.status_code}")
        except Exception as e:
            print(f"Keep alive error: {e}")
        time.sleep(600)  # 10 minutes

# Start keep alive thread
threading.Thread(target=keep_alive, daemon=True).start()
