import psycopg2
from psycopg2 import sql, extras
from bot.config import Config
import logging

logger = logging.getLogger(__name__)

class Database:
    """Database Connection Manager (Singleton)"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize database connection"""
        try:
            self.conn = psycopg2.connect(Config.DATABASE_URL, sslmode='require')
            self.conn.autocommit = False
            logger.info("✅ Database connected successfully")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    def get_connection(self):
        """Get database connection"""
        if self.conn.closed:
            self._initialize()
        return self.conn
    
    def close(self):
        """Close database connection"""
        if hasattr(self, 'conn') and not self.conn.closed:
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
    cursor.close()
    logger.info("✅ Database tables and indexes created")
