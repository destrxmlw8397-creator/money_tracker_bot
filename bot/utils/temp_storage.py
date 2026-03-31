import threading
import time
from datetime import datetime, timedelta
from typing import Any, Optional
from bot.config import Config

class TempStorage:
    """Temporary data storage with expiry"""
    
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
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """Start background cleanup thread"""
        def cleanup():
            while True:
                time.sleep(1800)  # 30 minutes
                self._cleanup_expired()
        
        thread = threading.Thread(target=cleanup, daemon=True)
        thread.start()
    
    def _cleanup_expired(self):
        """Remove expired data"""
        with self._lock:
            now = datetime.now()
            expired_ids = [tid for tid, item in self._data.items() 
                          if now > item['expires']]
            for tid in expired_ids:
                del self._data[tid]
            if expired_ids:
                print(f"🧹 Cleaned up {len(expired_ids)} expired temp data")
    
    def store(self, data: Any) -> str:
        """Store data and return ID"""
        with self._lock:
            self._counter += 1
            self._data[self._counter] = {
                'data': data,
                'expires': datetime.now() + timedelta(hours=Config.TEMP_DATA_EXPIRY_HOURS)
            }
            return str(self._counter)
    
    def get(self, temp_id: str) -> Optional[Any]:
        """Get and remove data by ID"""
        with self._lock:
            item = self._data.pop(int(temp_id), None)
            if item and datetime.now() < item['expires']:
                return item['data']
            return None

# Singleton instance
temp_storage = TempStorage()

def store_temp_data(data: Any) -> str:
    """Convenience function to store temp data"""
    return temp_storage.store(data)

def get_temp_data(temp_id: str) -> Optional[Any]:
    """Convenience function to get temp data"""
    return temp_storage.get(temp_id)
