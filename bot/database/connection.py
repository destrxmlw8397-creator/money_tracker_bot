import os
import psycopg2
from psycopg2 import sql, extras
from bot.config import Config
import logging
import time

logger = logging.getLogger(__name__)

class Database:
    """Database Connection Manager with retry logic for Render"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize database connection with retry"""
        self.conn = None
        self._connect_with_retry()
    
    def _connect_with_retry(self, max_retries=5, delay=5):
        """Connect to database with retry logic"""
        for attempt in range(max_retries):
            try:
                self.conn = psycopg2.connect(Config.DATABASE_URL, sslmode='require')
                self.conn.autocommit = False
                logger.info(f"✅ Database connected successfully (attempt {attempt + 1})")
                return
            except Exception as e:
                logger.warning(f"Database connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(delay)
                else:
                    logger.error("❌ All database connection attempts failed")
                    raise
    
    def get_connection(self):
        """Get database connection, reconnect if closed"""
        try:
            if self.conn is None or self.conn.closed:
                self._connect_with_retry()
            return self.conn
        except Exception as e:
            logger.error(f"Failed to get database connection: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if hasattr(self, 'conn') and self.conn and not self.conn.closed:
            self.conn.close()
            logger.info("Database connection closed")

def get_db_connection():
    """Get database connection (convenience function)"""
    db = Database()
    return db.get_connection()

def init_db():
    """Initialize database tables and indexes"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Create tables (same as before)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS balance_data (
                user_id BIGINT NOT NULL,
                month VARCHAR(20) NOT NULL,
                total_income DOUBLE PRECISION DEFAULT 0,
                total_expense DOUBLE PRECISION DEFAULT 0,
                budget_limit DOUBLE PRECISION DEFAULT 0,
                wallets JSONB DEFAULT '{"Cash": 0.0, "Bank": 0.0, "Bkash": 0.0}',
                history JSONB DEFAULT '[]',
                PRIMARY KEY (user_id, month)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS debt_data (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                name VARCHAR(255) NOT NULL,
                type VARCHAR(10) NOT NULL,
                amount DOUBLE PRECISION NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS debt_history (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                name VARCHAR(255) NOT NULL,
                amount DOUBLE PRECISION NOT NULL,
                date VARCHAR(20) NOT NULL,
                time VARCHAR(20) NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS outstanding_data (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                name VARCHAR(255) NOT NULL,
                type VARCHAR(10) NOT NULL,
                amount DOUBLE PRECISION NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS outstanding_history (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                name VARCHAR(255) NOT NULL,
                amount DOUBLE PRECISION NOT NULL,
                date VARCHAR(20) NOT NULL,
                time VARCHAR(20) NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS savings_goals (
                user_id BIGINT NOT NULL,
                name VARCHAR(255) NOT NULL,
                target DOUBLE PRECISION NOT NULL,
                saved DOUBLE PRECISION DEFAULT 0,
                PRIMARY KEY (user_id, name)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS goal_history (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                name VARCHAR(255) NOT NULL,
                amount DOUBLE PRECISION NOT NULL,
                date VARCHAR(20) NOT NULL,
                time VARCHAR(20) NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_language (
                user_id BIGINT PRIMARY KEY,
                lang VARCHAR(2) NOT NULL DEFAULT 'bn'
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_balance_user_month ON balance_data(user_id, month)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_debt_user_type ON debt_data(user_id, type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_debt_user_name ON debt_data(user_id, name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_debt_history_user_name ON debt_history(user_id, name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_goal_user_name ON savings_goals(user_id, name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_goal_history_user_name ON goal_history(user_id, name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_out_user_type ON outstanding_data(user_id, type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_out_user_name ON outstanding_data(user_id, name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_out_history_user_name ON outstanding_history(user_id, name)')
        
        conn.commit()
        logger.info("✅ Database tables and indexes created")
        
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
