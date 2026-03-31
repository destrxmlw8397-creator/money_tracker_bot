import threading
import time
from datetime import datetime, timedelta
from bot.config import Config

class TempStorage:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self._data = {}
        self._counter = 0
        self._lock = threading.Lock()
        self._start_cleanup()
    
    def _start_cleanup(self):
        def cleanup():
            while True:
                time.sleep(1800)
                with self._lock:
                    now = datetime.now()
                    expired = [tid for tid, item in self._data.items() if now > item['expires']]
                    for tid in expired:
                        del self._data[tid]
        threading.Thread(target=cleanup, daemon=True).start()
    
    def store(self, data):
        with self._lock:
            self._counter += 1
            self._data[self._counter] = {
                'data': data,
                'expires': datetime.now() + timedelta(hours=Config.TEMP_DATA_EXPIRY_HOURS)
            }
            return str(self._counter)
    
    def get(self, temp_id):
        with self._lock:
            item = self._data.pop(int(temp_id), None)
            if item and datetime.now() < item['expires']:
                return item['data']
            return None

temp_storage = TempStorage()

def store_temp_data(data):
    return temp_storage.store(data)

def get_temp_data(temp_id):
    return temp_storage.get(temp_id)
