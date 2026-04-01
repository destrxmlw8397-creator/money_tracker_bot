"""
Database Connection Module
Handles PostgreSQL connection with retry logic and connection pooling
"""

import time
import logging
import psycopg2
import json
from psycopg2 import pool, extras
from bot.config import Config

logger = logging.getLogger(__name__)


class Database:
    """
    Database connection manager with singleton pattern and connection pooling
    """
    
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize database connection pool with retry logic"""
        self._connect_with_retry()
    
    def _connect_with_retry(self, max_retries=5, delay=5):
        """
        Connect to database with retry logic
        
        Args:
            max_retries: Maximum number of connection attempts
            delay: Delay between attempts in seconds
        """
        for attempt in range(max_retries):
            try:
                self._pool = psycopg2.pool.SimpleConnectionPool(
                    1, 20,
                    dsn=Config.DATABASE_URL,
                    sslmode='require'
                )
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
        """
        Get a connection from the pool
        
        Returns:
            psycopg2 connection object
        """
        if self._pool is None:
            self._connect_with_retry()
        return self._pool.getconn()
    
    def put_connection(self, conn):
        """
        Return a connection to the pool
        
        Args:
            conn: psycopg2 connection to return
        """
        if self._pool and conn:
            self._pool.putconn(conn)
    
    def close(self):
        """Close all connections in the pool"""
        if self._pool:
            self._pool.closeall()
            logger.info("Database connection pool closed")


def get_db_connection():
    """
    Get database connection from pool
    
    Returns:
        psycopg2 connection object
    """
    db = Database()
    return db.get_connection()


def init_db():
    """
    Initialize database tables and indexes
    Creates all required tables if they don't exist
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Create balance_data table
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
        
        # Create debt_data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS debt_data (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                name VARCHAR(255) NOT NULL,
                type VARCHAR(10) NOT NULL,
                amount DOUBLE PRECISION NOT NULL
            )
        ''')
        
        # Create debt_history table
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
        
        # Create outstanding_data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS outstanding_data (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                name VARCHAR(255) NOT NULL,
                type VARCHAR(10) NOT NULL,
                amount DOUBLE PRECISION NOT NULL
            )
        ''')
        
        # Create outstanding_history table
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
        
        # Create savings_goals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS savings_goals (
                user_id BIGINT NOT NULL,
                name VARCHAR(255) NOT NULL,
                target DOUBLE PRECISION NOT NULL,
                saved DOUBLE PRECISION DEFAULT 0,
                PRIMARY KEY (user_id, name)
            )
        ''')
        
        # Create goal_history table
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
        
        # Create user_language table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_language (
                user_id BIGINT PRIMARY KEY,
                lang VARCHAR(2) NOT NULL DEFAULT 'bn'
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_balance_user_month ON balance_data(user_id, month)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_debt_user_type ON debt_data(user_id, type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_debt_user_name ON debt_data(user_id, name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_debt_history_user_name ON debt_history(user_id, name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_goal_user_name ON savings_goals(user_id, name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_goal_history_user_name ON goal_history(user_id, name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_out_user_type ON outstanding_data(user_id, type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_out_user_name ON outstanding_data(user_id, name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_out_history_user_name ON outstanding_history(user_id, name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_lang_user_id ON user_language(user_id)')
        
        conn.commit()
        logger.info("✅ Database tables and indexes created successfully")
        
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        db = Database()
        db.put_connection(conn)
