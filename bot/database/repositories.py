"""
Database Repository Module
Contains all CRUD operations for different data types
"""

import json
import logging
from bot.database.connection import get_db_connection, Database
from bot.config import Config

logger = logging.getLogger(__name__)


class BalanceRepository:
    """
    Repository for balance_data table operations
    Handles monthly balance, wallets, transactions
    """
    
    @staticmethod
    def get_monthly_data(user_id, month):
        """
        Get monthly data for a user, create if not exists
        
        Args:
            user_id: Telegram user ID
            month: Month in format "Jan-2026"
            
        Returns:
            dict: Monthly data with keys: user_id, month, total_income, total_expense,
                  budget_limit, wallets, history
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT * FROM balance_data WHERE user_id=%s AND month=%s",
                (user_id, month)
            )
            row = cursor.fetchone()
            
            if not row:
                # Create new monthly data
                default_wallets = json.dumps(Config.DEFAULT_WALLETS)
                cursor.execute(
                    "INSERT INTO balance_data (user_id, month, wallets, history) VALUES (%s, %s, %s, %s)",
                    (user_id, month, default_wallets, '[]')
                )
                conn.commit()
                
                cursor.execute(
                    "SELECT * FROM balance_data WHERE user_id=%s AND month=%s",
                    (user_id, month)
                )
                row = cursor.fetchone()
            
            data = {
                'user_id': row[0],
                'month': row[1],
                'total_income': row[2],
                'total_expense': row[3],
                'budget_limit': row[4],
                'wallets': row[5] if isinstance(row[5], dict) else json.loads(row[5]),
                'history': row[6] if isinstance(row[6], list) else json.loads(row[6])
            }
            
            conn.commit()
            return data
            
        except Exception as e:
            logger.error(f"Error in get_monthly_data: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)
    
    @staticmethod
    def update_monthly_data(user_id, month, data):
        """
        Update monthly data for a user
        
        Args:
            user_id: Telegram user ID
            month: Month in format "Jan-2026"
            data: Dictionary containing updated data
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """UPDATE balance_data 
                   SET total_income=%s, total_expense=%s, budget_limit=%s, wallets=%s, history=%s 
                   WHERE user_id=%s AND month=%s""",
                (
                    data['total_income'],
                    data['total_expense'],
                    data['budget_limit'],
                    json.dumps(data['wallets']),
                    json.dumps(data['history']),
                    user_id,
                    month
                )
            )
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error in update_monthly_data: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)
    
    @staticmethod
    def get_all_months(user_id):
        """
        Get all months data for a user
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            list: List of monthly data dictionaries
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM balance_data WHERE user_id=%s", (user_id,))
            rows = cursor.fetchall()
            
            all_data = []
            for row in rows:
                all_data.append({
                    'user_id': row[0],
                    'month': row[1],
                    'total_income': row[2],
                    'total_expense': row[3],
                    'budget_limit': row[4],
                    'wallets': row[5] if isinstance(row[5], dict) else json.loads(row[5]),
                    'history': row[6] if isinstance(row[6], list) else json.loads(row[6])
                })
            
            conn.commit()
            return all_data
            
        except Exception as e:
            logger.error(f"Error in get_all_months: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)
    
    @staticmethod
    def delete_user_data(user_id):
        """
        Delete all balance data for a user
        
        Args:
            user_id: Telegram user ID
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM balance_data WHERE user_id=%s", (user_id,))
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error in delete_user_data: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)
    
    @staticmethod
    def delete_month_data(user_id, month):
        """
        Reset monthly data to default values
        
        Args:
            user_id: Telegram user ID
            month: Month in format "Jan-2026"
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            default_wallets = json.dumps(Config.DEFAULT_WALLETS)
            cursor.execute(
                """UPDATE balance_data 
                   SET total_income=0, total_expense=0, history='[]', wallets=%s 
                   WHERE user_id=%s AND month=%s""",
                (default_wallets, user_id, month)
            )
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error in delete_month_data: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)


class DebtRepository:
    """
    Repository for debt_data table operations
    Handles loan and debt entries (give/take)
    """
    
    @staticmethod
    def get_all(user_id):
        """
        Get all debts for a user
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            list: List of debt dictionaries
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM debt_data WHERE user_id=%s", (user_id,))
            rows = cursor.fetchall()
            conn.commit()
            
            return [
                {
                    'id': r[0],
                    'user_id': r[1],
                    'name': r[2],
                    'type': r[3],
                    'amount': r[4]
                }
                for r in rows
            ]
            
        except Exception as e:
            logger.error(f"Error in get_all: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)
    
    @staticmethod
    def get_by_type(user_id, debt_type):
        """
        Get debts by type (give or take)
        
        Args:
            user_id: Telegram user ID
            debt_type: 'give' or 'take'
            
        Returns:
            list: List of debt dictionaries
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT * FROM debt_data WHERE user_id=%s AND type=%s",
                (user_id, debt_type)
            )
            rows = cursor.fetchall()
            conn.commit()
            
            return [
                {
                    'id': r[0],
                    'user_id': r[1],
                    'name': r[2],
                    'type': r[3],
                    'amount': r[4]
                }
                for r in rows
            ]
            
        except Exception as e:
            logger.error(f"Error in get_by_type: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)
    
    @staticmethod
    def get_distinct_names(user_id, debt_type):
        """
        Get distinct names for a debt type
        
        Args:
            user_id: Telegram user ID
            debt_type: 'give' or 'take'
            
        Returns:
            list: List of unique names
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT DISTINCT name FROM debt_data WHERE user_id=%s AND type=%s",
                (user_id, debt_type)
            )
            names = [row[0] for row in cursor.fetchall()]
            conn.commit()
            return names
            
        except Exception as e:
            logger.error(f"Error in get_distinct_names: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)
    
    @staticmethod
    def add_or_update(user_id, name, debt_type, amount):
        """
        Add new debt or update existing one
        
        Args:
            user_id: Telegram user ID
            name: Person name
            debt_type: 'give' or 'take'
            amount: Amount to add (positive)
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT id FROM debt_data WHERE user_id=%s AND name=%s AND type=%s",
                (user_id, name, debt_type)
            )
            row = cursor.fetchone()
            
            if row:
                cursor.execute(
                    "UPDATE debt_data SET amount = amount + %s WHERE id=%s",
                    (amount, row[0])
                )
            else:
                cursor.execute(
                    "INSERT INTO debt_data (user_id, name, type, amount) VALUES (%s,%s,%s,%s)",
                    (user_id, name, debt_type, amount)
                )
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error in add_or_update: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)
    
    @staticmethod
    def update_amount(debt_id, new_amount):
        """
        Update debt amount
        
        Args:
            debt_id: Debt record ID
            new_amount: New amount value
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "UPDATE debt_data SET amount=%s WHERE id=%s",
                (new_amount, debt_id)
            )
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error in update_amount: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)
    
    @staticmethod
    def get_by_id(debt_id):
        """
        Get debt by ID
        
        Args:
            debt_id: Debt record ID
            
        Returns:
            dict: Debt dictionary or None
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM debt_data WHERE id=%s", (debt_id,))
            row = cursor.fetchone()
            conn.commit()
            
            if row:
                return {
                    'id': row[0],
                    'user_id': row[1],
                    'name': row[2],
                    'type': row[3],
                    'amount': row[4]
                }
            return None
            
        except Exception as e:
            logger.error(f"Error in get_by_id: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)
    
    @staticmethod
    def delete_by_name(user_id, name):
        """
        Delete all debts by person name
        
        Args:
            user_id: Telegram user ID
            name: Person name
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "DELETE FROM debt_data WHERE user_id=%s AND name=%s",
                (user_id, name)
            )
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error in delete_by_name: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)
    
    @staticmethod
    def delete_user_data(user_id):
        """
        Delete all debt data for a user
        
        Args:
            user_id: Telegram user ID
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM debt_data WHERE user_id=%s", (user_id,))
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error in delete_user_data: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)


class DebtHistoryRepository:
    """
    Repository for debt_history table operations
    Stores transaction history for debts
    """
    
    @staticmethod
    def add(user_id, name, amount, date, time):
        """
        Add debt history entry
        
        Args:
            user_id: Telegram user ID
            name: Person name
            amount: Transaction amount (positive for give, negative for repayment)
            date: Date string (DD-MM-YYYY)
            time: Time string (HH:MM)
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO debt_history (user_id, name, amount, date, time) VALUES (%s,%s,%s,%s,%s)",
                (user_id, name, amount, date, time)
            )
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error in add: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)
    
    @staticmethod
    def get_by_name(user_id, name, limit=10, offset=0):
        """
        Get debt history by person name with pagination
        
        Args:
            user_id: Telegram user ID
            name: Person name
            limit: Number of records per page
            offset: Offset for pagination
            
        Returns:
            tuple: (list of history entries, total count)
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT * FROM debt_history WHERE user_id=%s AND name=%s ORDER BY id DESC LIMIT %s OFFSET %s",
                (user_id, name, limit, offset)
            )
            rows = cursor.fetchall()
            
            cursor.execute(
                "SELECT COUNT(*) FROM debt_history WHERE user_id=%s AND name=%s",
                (user_id, name)
            )
            total = cursor.fetchone()[0]
            
            conn.commit()
            
            history = [
                {
                    'id': r[0],
                    'user_id': r[1],
                    'name': r[2],
                    'amount': r[3],
                    'date': r[4],
                    'time': r[5]
                }
                for r in rows
            ]
            
            return history, total
            
        except Exception as e:
            logger.error(f"Error in get_by_name: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)
    
    @staticmethod
    def delete_by_name(user_id, name):
        """
        Delete all debt history by person name
        
        Args:
            user_id: Telegram user ID
            name: Person name
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "DELETE FROM debt_history WHERE user_id=%s AND name=%s",
                (user_id, name)
            )
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error in delete_by_name: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)
    
    @staticmethod
    def delete_user_data(user_id):
        """
        Delete all debt history for a user
        
        Args:
            user_id: Telegram user ID
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM debt_history WHERE user_id=%s", (user_id,))
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error in delete_user_data: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)


class OutstandingRepository:
    """
    Repository for outstanding_data table operations
    Handles work-related payments (doesn't affect main balance until repayment)
    """
    
    @staticmethod
    def get_all(user_id):
        """
        Get all outstanding entries for a user
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            list: List of outstanding dictionaries
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM outstanding_data WHERE user_id=%s", (user_id,))
            rows = cursor.fetchall()
            conn.commit()
            
            return [
                {
                    'id': r[0],
                    'user_id': r[1],
                    'name': r[2],
                    'type': r[3],
                    'amount': r[4]
                }
                for r in rows
            ]
            
        except Exception as e:
            logger.error(f"Error in get_all: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)
    
    @staticmethod
    def get_by_type(user_id, out_type):
        """
        Get outstanding entries by type (give or take)
        
        Args:
            user_id: Telegram user ID
            out_type: 'give' or 'take'
            
        Returns:
            list: List of outstanding dictionaries
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT * FROM outstanding_data WHERE user_id=%s AND type=%s",
                (user_id, out_type)
            )
            rows = cursor.fetchall()
            conn.commit()
            
            return [
                {
                    'id': r[0],
                    'user_id': r[1],
                    'name': r[2],
                    'type': r[3],
                    'amount': r[4]
                }
                for r in rows
            ]
            
        except Exception as e:
            logger.error(f"Error in get_by_type: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)
    
    @staticmethod
    def get_distinct_names(user_id, out_type):
        """
        Get distinct names for outstanding type
        
        Args:
            user_id: Telegram user ID
            out_type: 'give' or 'take'
            
        Returns:
            list: List of unique names
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT DISTINCT name FROM outstanding_data WHERE user_id=%s AND type=%s",
                (user_id, out_type)
            )
            names = [row[0] for row in cursor.fetchall()]
            conn.commit()
            return names
            
        except Exception as e:
            logger.error(f"Error in get_distinct_names: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)
    
    @staticmethod
    def add_or_update(user_id, name, out_type, amount):
        """
        Add new outstanding entry or update existing one
        
        Args:
            user_id: Telegram user ID
            name: Person name
            out_type: 'give' or 'take'
            amount: Amount to add (positive)
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT id FROM outstanding_data WHERE user_id=%s AND name=%s AND type=%s",
                (user_id, name, out_type)
            )
            row = cursor.fetchone()
            
            if row:
                cursor.execute(
                    "UPDATE outstanding_data SET amount = amount + %s WHERE id=%s",
                    (amount, row[0])
                )
            else:
                cursor.execute(
                    "INSERT INTO outstanding_data (user_id, name, type, amount) VALUES (%s,%s,%s,%s)",
                    (user_id, name, out_type, amount)
                )
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error in add_or_update: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)
    
    @staticmethod
    def update_amount(out_id, new_amount):
        """
        Update outstanding amount
        
        Args:
            out_id: Outstanding record ID
            new_amount: New amount value
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "UPDATE outstanding_data SET amount=%s WHERE id=%s",
                (new_amount, out_id)
            )
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error in update_amount: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)
    
    @staticmethod
    def get_by_id(out_id):
        """
        Get outstanding entry by ID
        
        Args:
            out_id: Outstanding record ID
            
        Returns:
            dict: Outstanding dictionary or None
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM outstanding_data WHERE id=%s", (out_id,))
            row = cursor.fetchone()
            conn.commit()
            
            if row:
                return {
                    'id': row[0],
                    'user_id': row[1],
                    'name': row[2],
                    'type': row[3],
                    'amount': row[4]
                }
            return None
            
        except Exception as e:
            logger.error(f"Error in get_by_id: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)
    
    @staticmethod
    def delete_by_name(user_id, name):
        """
        Delete all outstanding entries by person name
        
        Args:
            user_id: Telegram user ID
            name: Person name
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "DELETE FROM outstanding_data WHERE user_id=%s AND name=%s",
                (user_id, name)
            )
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error in delete_by_name: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)
    
    @staticmethod
    def delete_user_data(user_id):
        """
        Delete all outstanding data for a user
        
        Args:
            user_id: Telegram user ID
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM outstanding_data WHERE user_id=%s", (user_id,))
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error in delete_user_data: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)


class OutstandingHistoryRepository:
    """
    Repository for outstanding_history table operations
    Stores transaction history for outstanding payments
    """
    
    @staticmethod
    def add(user_id, name, amount, date, time):
        """
        Add outstanding history entry
        
        Args:
            user_id: Telegram user ID
            name: Person name
            amount: Transaction amount
            date: Date string (DD-MM-YYYY)
            time: Time string (HH:MM)
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO outstanding_history (user_id, name, amount, date, time) VALUES (%s,%s,%s,%s,%s)",
                (user_id, name, amount, date, time)
            )
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error in add: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)
    
    @staticmethod
    def get_by_name(user_id, name):
        """
        Get outstanding history by person name
        
        Args:
            user_id: Telegram user ID
            name: Person name
            
        Returns:
            list: List of history entries
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT * FROM outstanding_history WHERE user_id=%s AND name=%s ORDER BY id DESC",
                (user_id, name)
            )
            rows = cursor.fetchall()
            conn.commit()
            
            return [
                {
                    'id': r[0],
                    'user_id': r[1],
                    'name': r[2],
                    'amount': r[3],
                    'date': r[4],
                    'time': r[5]
                }
                for r in rows
            ]
            
        except Exception as e:
            logger.error(f"Error in get_by_name: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)
    
    @staticmethod
    def delete_by_name(user_id, name):
        """
        Delete all outstanding history by person name
        
        Args:
            user_id: Telegram user ID
            name: Person name
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "DELETE FROM outstanding_history WHERE user_id=%s AND name=%s",
                (user_id, name)
            )
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error in delete_by_name: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)
    
    @staticmethod
    def delete_user_data(user_id):
        """
        Delete all outstanding history for a user
        
        Args:
            user_id: Telegram user ID
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM outstanding_history WHERE user_id=%s", (user_id,))
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error in delete_user_data: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)


class GoalRepository:
    """
    Repository for savings_goals table operations
    Handles savings goals management
    """
    
    @staticmethod
    def get_all(user_id):
        """
        Get all savings goals for a user
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            list: List of goal dictionaries
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM savings_goals WHERE user_id=%s", (user_id,))
            rows = cursor.fetchall()
            conn.commit()
            
            return [
                {
                    'user_id': r[0],
                    'name': r[1],
                    'target': r[2],
                    'saved': r[3]
                }
                for r in rows
            ]
            
        except Exception as e:
            logger.error(f"Error in get_all: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)
    
    @staticmethod
    def add_or_update(user_id, name, target):
        """
        Add new goal or update existing one
        
        Args:
            user_id: Telegram user ID
            name: Goal name
            target: Target amount
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO savings_goals (user_id, name, target, saved) VALUES (%s, %s, %s, 0) ON CONFLICT (user_id, name) DO UPDATE SET target=%s",
                (user_id, name, target, target)
            )
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error in add_or_update: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)
    
    @staticmethod
    def add_savings(user_id, name, amount):
        """
        Add savings to a goal
        
        Args:
            user_id: Telegram user ID
            name: Goal name
            amount: Amount to add
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "UPDATE savings_goals SET saved = saved + %s WHERE user_id=%s AND name=%s",
                (amount, user_id, name)
            )
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error in add_savings: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)
    
    @staticmethod
    def delete_by_name(user_id, name):
        """
        Delete a goal by name
        
        Args:
            user_id: Telegram user ID
            name: Goal name
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "DELETE FROM savings_goals WHERE user_id=%s AND name=%s",
                (user_id, name)
            )
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error in delete_by_name: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)
    
    @staticmethod
    def delete_user_data(user_id):
        """
        Delete all savings goals for a user
        
        Args:
            user_id: Telegram user ID
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM savings_goals WHERE user_id=%s", (user_id,))
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error in delete_user_data: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)


class GoalHistoryRepository:
    """
    Repository for goal_history table operations
    Stores savings transaction history for goals
    """
    
    @staticmethod
    def add(user_id, name, amount, date, time):
        """
        Add goal history entry
        
        Args:
            user_id: Telegram user ID
            name: Goal name
            amount: Amount saved
            date: Date string (DD-MM-YYYY)
            time: Time string (HH:MM)
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO goal_history (user_id, name, amount, date, time) VALUES (%s,%s,%s,%s,%s)",
                (user_id, name, amount, date, time)
            )
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error in add: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)
    
    @staticmethod
    def get_by_name(user_id, name, limit=10):
        """
        Get goal history by goal name
        
        Args:
            user_id: Telegram user ID
            name: Goal name
            limit: Maximum number of records to return
            
        Returns:
            list: List of history entries
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT * FROM goal_history WHERE user_id=%s AND name=%s ORDER BY id DESC LIMIT %s",
                (user_id, name, limit)
            )
            rows = cursor.fetchall()
            conn.commit()
            
            return [
                {
                    'id': r[0],
                    'user_id': r[1],
                    'name': r[2],
                    'amount': r[3],
                    'date': r[4],
                    'time': r[5]
                }
                for r in rows
            ]
            
        except Exception as e:
            logger.error(f"Error in get_by_name: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)
    
    @staticmethod
    def delete_by_name(user_id, name):
        """
        Delete all goal history by goal name
        
        Args:
            user_id: Telegram user ID
            name: Goal name
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "DELETE FROM goal_history WHERE user_id=%s AND name=%s",
                (user_id, name)
            )
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error in delete_by_name: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)
    
    @staticmethod
    def delete_user_data(user_id):
        """
        Delete all goal history for a user
        
        Args:
            user_id: Telegram user ID
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM goal_history WHERE user_id=%s", (user_id,))
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error in delete_user_data: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)


class UserRepository:
    """
    Repository for user_language table operations
    Handles user language preferences
    """
    
    @staticmethod
    def get_language(user_id):
        """
        Get user language preference
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            str: Language code ('bn' or 'en'), defaults to 'bn'
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT lang FROM user_language WHERE user_id=%s", (user_id,))
            row = cursor.fetchone()
            conn.commit()
            return row[0] if row else "bn"
            
        except Exception as e:
            logger.error(f"Error in get_language: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)
    
    @staticmethod
    def set_language(user_id, lang):
        """
        Set user language preference
        
        Args:
            user_id: Telegram user ID
            lang: Language code ('bn' or 'en')
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO user_language (user_id, lang) VALUES (%s, %s) ON CONFLICT (user_id) DO UPDATE SET lang=%s",
                (user_id, lang, lang)
            )
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error in set_language: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            db = Database()
            db.put_connection(conn)
