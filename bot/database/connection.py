import os
import psycopg2
from psycopg2 import pool, extras
import logging
import time
import json
from bot.config import Config

logger = logging.getLogger(__name__)

class Database:
    """Database connection manager with connection pooling"""
    
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize connection pool with retry logic"""
        max_retries = 5
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                self._pool = psycopg2.pool.SimpleConnectionPool(
                    1, 20,
                    dsn=Config.DATABASE_URL,
                    sslmode='require'
                )
                logger.info(f"✅ Database pool created (attempt {attempt + 1})")
                return
            except Exception as e:
                logger.warning(f"DB connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    logger.error("❌ All database connection attempts failed")
                    raise
    
    def get_connection(self):
        """Get connection from pool"""
        if self._pool is None:
            self._initialize()
        return self._pool.getconn()
    
    def put_connection(self, conn):
        """Return connection to pool"""
        if self._pool:
            self._pool.putconn(conn)
    
    def close(self):
        """Close all connections"""
        if self._pool:
            self._pool.closeall()
            logger.info("Database pool closed")

_db = Database()

def get_db_connection():
    """Get database connection"""
    return _db.get_connection()

def return_connection(conn):
    """Return connection to pool"""
    _db.put_connection(conn)

def init_db():
    """Initialize database tables and indexes"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Create tables
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
        _db.put_connection(conn)
