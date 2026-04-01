"""
Temporary Storage Module
Stores temporary callback data with automatic expiration (12 hours)
"""

import threading
import time
from datetime import datetime, timedelta
from typing import Any, Optional
from bot.config import Config


class TempStorage:
    """
    Thread-safe temporary storage with automatic expiration
    
    Stores data temporarily for callback handling (like wallet selection,
    amount input, etc.). Data expires after 12 hours.
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern implementation"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize storage and start cleanup thread"""
        self._data = {}
        self._counter = 0
        self._lock = threading.Lock()
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """
        Start background thread to clean up expired data
        Runs every 30 minutes
        """
        def cleanup_worker():
            while True:
                time.sleep(1800)  # 30 minutes
                self._cleanup_expired()
        
        thread = threading.Thread(target=cleanup_worker, daemon=True)
        thread.start()
    
    def _cleanup_expired(self):
        """
        Remove all expired data entries
        Called automatically every 30 minutes
        """
        with self._lock:
            now = datetime.now()
            expired_ids = [
                tid for tid, item in self._data.items()
                if now > item['expires']
            ]
            
            for tid in expired_ids:
                del self._data[tid]
            
            if expired_ids:
                print(f"🧹 Cleaned up {len(expired_ids)} expired temp data")
    
    def store(self, data: Any) -> str:
        """
        Store data and return a unique ID
        
        Args:
            data: Any data to store (will be retrieved later)
            
        Returns:
            str: Unique ID for retrieving the data
        """
        with self._lock:
            self._counter += 1
            self._data[self._counter] = {
                'data': data,
                'expires': datetime.now() + timedelta(hours=Config.TEMP_DATA_EXPIRY_HOURS)
            }
            return str(self._counter)
    
    def get(self, temp_id: str) -> Optional[Any]:
        """
        Retrieve and remove data by ID
        
        Args:
            temp_id: The ID returned by store()
            
        Returns:
            Any: The stored data if exists and not expired, None otherwise
        """
        with self._lock:
            try:
                item = self._data.pop(int(temp_id), None)
                if item and datetime.now() < item['expires']:
                    return item['data']
            except (ValueError, KeyError):
                pass
            return None
    
    def clear_all(self):
        """Clear all stored data (for testing/emergency)"""
        with self._lock:
            self._data.clear()
            self._counter = 0


# Singleton instance for easy import
_temp_storage = None


def get_temp_storage() -> TempStorage:
    """Get the singleton TempStorage instance"""
    global _temp_storage
    if _temp_storage is None:
        _temp_storage = TempStorage()
    return _temp_storage


def store_temp_data(data: Any) -> str:
    """
    Store temporary data and return ID
    
    Args:
        data: Any data to store
        
    Returns:
        str: Unique ID for retrieval
    """
    return get_temp_storage().store(data)


def get_temp_data(temp_id: str) -> Optional[Any]:
    """
    Retrieve and remove temporary data by ID
    
    Args:
        temp_id: ID returned by store_temp_data()
        
    Returns:
        Any: Stored data or None if expired/invalid
    """
    return get_temp_storage().get(temp_id)


def clear_all_temp_data():
    """Clear all temporary data (useful for testing)"""
    get_temp_storage().clear_all()
