import json
from typing import List, Dict, Optional, Any
from bot.database.connection import get_db_connection, return_connection
from bot.config import Config
import logging

logger = logging.getLogger(__name__)

class BalanceRepository:
    """Balance data repository - MongoDB থেকে PostgreSQL এ রূপান্তরিত"""
    
    @staticmethod
    def get_monthly_data(user_id: int, month: str) -> Dict[str, Any]:
        """Get monthly data for a user"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
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
        
        cursor.close()
        return_connection(conn)
        return data
    
    @staticmethod
    def update_monthly_data(user_id: int, month: str, data: Dict[str, Any]):
        """Update monthly data"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """UPDATE balance_data 
               SET total_income=%s, total_expense=%s, budget_limit=%s, wallets=%s, history=%s 
               WHERE user_id=%s AND month=%s""",
            (data.get('total_income', 0), data.get('total_expense', 0),
             data.get('budget_limit', 0), json.dumps(data.get('wallets', {})),
             json.dumps(data.get('history', [])), user_id, month)
        )
        
        conn.commit()
        cursor.close()
        return_connection(conn)
    
    @staticmethod
    def add_transaction(user_id: int, month: str, transaction: Dict, inc_income: float, inc_expense: float):
        """Add transaction to history"""
        data = BalanceRepository.get_monthly_data(user_id, month)
        data['history'].append(transaction)
        data['wallets'][transaction['wallet']] = data['wallets'].get(transaction['wallet'], 0) + transaction['amount']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """UPDATE balance_data 
               SET total_income=total_income+%s, total_expense=total_expense+%s, wallets=%s, history=%s 
               WHERE user_id=%s AND month=%s""",
            (inc_income, inc_expense, json.dumps(data['wallets']),
             json.dumps(data['history']), user_id, month)
        )
        
        conn.commit()
        cursor.close()
        return_connection(conn)
    
    @staticmethod
    def get_all_months(user_id: int) -> List[Dict]:
        """Get all months data for a user"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM balance_data WHERE user_id=%s", (user_id,))
        rows = cursor.fetchall()
        
        all_data = []
        for row in rows:
            data = {
                'user_id': row[0],
                'month': row[1],
                'total_income': row[2],
                'total_expense': row[3],
                'budget_limit': row[4],
                'wallets': row[5] if isinstance(row[5], dict) else json.loads(row[5]),
                'history': row[6] if isinstance(row[6], list) else json.loads(row[6])
            }
            all_data.append(data)
        
        cursor.close()
        return_connection(conn)
        return all_data
    
    @staticmethod
    def delete_user_data(user_id: int):
        """Delete all user data"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM balance_data WHERE user_id=%s", (user_id,))
        conn.commit()
        cursor.close()
        return_connection(conn)
    
    @staticmethod
    def delete_month_data(user_id: int, month: str):
        """Delete specific month data"""
        conn = get_db_connection()
        cursor = conn.cursor()
        default_wallets = json.dumps(Config.DEFAULT_WALLETS)
        cursor.execute(
            "UPDATE balance_data SET total_income=0, total_expense=0, history='[]', wallets=%s WHERE user_id=%s AND month=%s",
            (default_wallets, user_id, month)
        )
        conn.commit()
        cursor.close()
        return_connection(conn)


class DebtRepository:
    """Debt data repository - MongoDB থেকে PostgreSQL এ রূপান্তরিত"""
    
    @staticmethod
    def get_all(user_id: int) -> List[Dict]:
        """Get all debts for a user"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM debt_data WHERE user_id=%s", (user_id,))
        rows = cursor.fetchall()
        cursor.close()
        return_connection(conn)
        
        return [{'id': r[0], 'user_id': r[1], 'name': r[2], 'type': r[3], 'amount': r[4]} for r in rows]
    
    @staticmethod
    def get_by_type(user_id: int, debt_type: str) -> List[Dict]:
        """Get debts by type"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM debt_data WHERE user_id=%s AND type=%s",
            (user_id, debt_type)
        )
        rows = cursor.fetchall()
        cursor.close()
        return_connection(conn)
        
        return [{'id': r[0], 'user_id': r[1], 'name': r[2], 'type': r[3], 'amount': r[4]} for r in rows]
    
    @staticmethod
    def get_distinct_names(user_id: int, debt_type: str) -> List[str]:
        """Get distinct names by type"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT DISTINCT name FROM debt_data WHERE user_id=%s AND type=%s",
            (user_id, debt_type)
        )
        names = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return_connection(conn)
        return names
    
    @staticmethod
    def add_or_update(user_id: int, name: str, debt_type: str, amount: float):
        """Add or update debt"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
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
        cursor.close()
        return_connection(conn)
    
    @staticmethod
    def update_amount(debt_id: int, new_amount: float):
        """Update debt amount"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE debt_data SET amount=%s WHERE id=%s",
            (new_amount, debt_id)
        )
        conn.commit()
        cursor.close()
        return_connection(conn)
    
    @staticmethod
    def get_by_id(debt_id: int) -> Optional[Dict]:
        """Get debt by ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM debt_data WHERE id=%s", (debt_id,))
        row = cursor.fetchone()
        cursor.close()
        return_connection(conn)
        
        if row:
            return {'id': row[0], 'user_id': row[1], 'name': row[2], 'type': row[3], 'amount': row[4]}
        return None
    
    @staticmethod
    def delete_by_name(user_id: int, name: str):
        """Delete all debts by name"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM debt_data WHERE user_id=%s AND name=%s",
            (user_id, name)
        )
        conn.commit()
        cursor.close()
        return_connection(conn)
    
    @staticmethod
    def delete_user_data(user_id: int):
        """Delete all user debt data"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM debt_data WHERE user_id=%s", (user_id,))
        conn.commit()
        cursor.close()
        return_connection(conn)


class DebtHistoryRepository:
    """Debt history repository"""
    
    @staticmethod
    def add(user_id: int, name: str, amount: float, date: str, time: str):
        """Add debt history entry"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO debt_history (user_id, name, amount, date, time) VALUES (%s,%s,%s,%s,%s)",
            (user_id, name, amount, date, time)
        )
        conn.commit()
        cursor.close()
        return_connection(conn)
    
    @staticmethod
    def get_by_name(user_id: int, name: str, limit: int = 10, offset: int = 0) -> tuple:
        """Get history by name"""
        conn = get_db_connection()
        cursor = conn.cursor()
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
        
        cursor.close()
        return_connection(conn)
        
        history = [{'id': r[0], 'user_id': r[1], 'name': r[2], 'amount': r[3], 'date': r[4], 'time': r[5]} for r in rows]
        return history, total
    
    @staticmethod
    def delete_by_name(user_id: int, name: str):
        """Delete all history by name"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM debt_history WHERE user_id=%s AND name=%s",
            (user_id, name)
        )
        conn.commit()
        cursor.close()
        return_connection(conn)
    
    @staticmethod
    def delete_user_data(user_id: int):
        """Delete all user debt history"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM debt_history WHERE user_id=%s", (user_id,))
        conn.commit()
        cursor.close()
        return_connection(conn)


class OutstandingRepository:
    """Outstanding data repository"""
    
    @staticmethod
    def get_by_type(user_id: int, out_type: str) -> List[Dict]:
        """Get outstanding by type"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM outstanding_data WHERE user_id=%s AND type=%s",
            (user_id, out_type)
        )
        rows = cursor.fetchall()
        cursor.close()
        return_connection(conn)
        
        return [{'id': r[0], 'user_id': r[1], 'name': r[2], 'type': r[3], 'amount': r[4]} for r in rows]
    
    @staticmethod
    def get_distinct_names(user_id: int, out_type: str) -> List[str]:
        """Get distinct names by type"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT DISTINCT name FROM outstanding_data WHERE user_id=%s AND type=%s",
            (user_id, out_type)
        )
        names = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return_connection(conn)
        return names
    
    @staticmethod
    def add_or_update(user_id: int, name: str, out_type: str, amount: float):
        """Add or update outstanding"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
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
        cursor.close()
        return_connection(conn)
    
    @staticmethod
    def update_amount(out_id: int, new_amount: float):
        """Update outstanding amount"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE outstanding_data SET amount=%s WHERE id=%s",
            (new_amount, out_id)
        )
        conn.commit()
        cursor.close()
        return_connection(conn)
    
    @staticmethod
    def get_by_id(out_id: int) -> Optional[Dict]:
        """Get outstanding by ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM outstanding_data WHERE id=%s", (out_id,))
        row = cursor.fetchone()
        cursor.close()
        return_connection(conn)
        
        if row:
            return {'id': row[0], 'user_id': row[1], 'name': row[2], 'type': row[3], 'amount': row[4]}
        return None
    
    @staticmethod
    def get_all(user_id: int) -> List[Dict]:
        """Get all outstanding for a user"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM outstanding_data WHERE user_id=%s", (user_id,))
        rows = cursor.fetchall()
        cursor.close()
        return_connection(conn)
        
        return [{'id': r[0], 'user_id': r[1], 'name': r[2], 'type': r[3], 'amount': r[4]} for r in rows]
    
    @staticmethod
    def delete_by_name(user_id: int, name: str):
        """Delete all outstanding by name"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM outstanding_data WHERE user_id=%s AND name=%s",
            (user_id, name)
        )
        conn.commit()
        cursor.close()
        return_connection(conn)
    
    @staticmethod
    def delete_user_data(user_id: int):
        """Delete all user outstanding data"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM outstanding_data WHERE user_id=%s", (user_id,))
        conn.commit()
        cursor.close()
        return_connection(conn)


class OutstandingHistoryRepository:
    """Outstanding history repository"""
    
    @staticmethod
    def add(user_id: int, name: str, amount: float, date: str, time: str):
        """Add outstanding history entry"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO outstanding_history (user_id, name, amount, date, time) VALUES (%s,%s,%s,%s,%s)",
            (user_id, name, amount, date, time)
        )
        conn.commit()
        cursor.close()
        return_connection(conn)
    
    @staticmethod
    def get_by_name(user_id: int, name: str, limit: int = 10, offset: int = 0) -> List[Dict]:
        """Get history by name"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM outstanding_history WHERE user_id=%s AND name=%s ORDER BY id DESC LIMIT %s OFFSET %s",
            (user_id, name, limit, offset)
        )
        rows = cursor.fetchall()
        cursor.close()
        return_connection(conn)
        
        return [{'id': r[0], 'user_id': r[1], 'name': r[2], 'amount': r[3], 'date': r[4], 'time': r[5]} for r in rows]
    
    @staticmethod
    def delete_by_name(user_id: int, name: str):
        """Delete all history by name"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM outstanding_history WHERE user_id=%s AND name=%s",
            (user_id, name)
        )
        conn.commit()
        cursor.close()
        return_connection(conn)
    
    @staticmethod
    def delete_user_data(user_id: int):
        """Delete all user outstanding history"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM outstanding_history WHERE user_id=%s", (user_id,))
        conn.commit()
        cursor.close()
        return_connection(conn)


class GoalRepository:
    """Savings goal repository"""
    
    @staticmethod
    def get_all(user_id: int) -> List[Dict]:
        """Get all goals for a user"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM savings_goals WHERE user_id=%s", (user_id,))
        rows = cursor.fetchall()
        cursor.close()
        return_connection(conn)
        
        return [{'user_id': r[0], 'name': r[1], 'target': r[2], 'saved': r[3]} for r in rows]
    
    @staticmethod
    def add_or_update(user_id: int, name: str, target: float):
        """Add or update goal"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO savings_goals (user_id, name, target, saved) VALUES (%s, %s, %s, 0) ON CONFLICT (user_id, name) DO UPDATE SET target=%s",
            (user_id, name, target, target)
        )
        conn.commit()
        cursor.close()
        return_connection(conn)
    
    @staticmethod
    def add_savings(user_id: int, name: str, amount: float):
        """Add savings to goal"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE savings_goals SET saved = saved + %s WHERE user_id=%s AND name=%s",
            (amount, user_id, name)
        )
        conn.commit()
        cursor.close()
        return_connection(conn)
    
    @staticmethod
    def get_by_name(user_id: int, name: str) -> Optional[Dict]:
        """Get goal by name"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM savings_goals WHERE user_id=%s AND name=%s",
            (user_id, name)
        )
        row = cursor.fetchone()
        cursor.close()
        return_connection(conn)
        
        if row:
            return {'user_id': row[0], 'name': row[1], 'target': row[2], 'saved': row[3]}
        return None
    
    @staticmethod
    def delete_by_name(user_id: int, name: str):
        """Delete goal by name"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM savings_goals WHERE user_id=%s AND name=%s",
            (user_id, name)
        )
        conn.commit()
        cursor.close()
        return_connection(conn)
    
    @staticmethod
    def delete_user_data(user_id: int):
        """Delete all user goals"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM savings_goals WHERE user_id=%s", (user_id,))
        conn.commit()
        cursor.close()
        return_connection(conn)


class GoalHistoryRepository:
    """Goal history repository"""
    
    @staticmethod
    def add(user_id: int, name: str, amount: float, date: str, time: str):
        """Add goal history entry"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO goal_history (user_id, name, amount, date, time) VALUES (%s,%s,%s,%s,%s)",
            (user_id, name, amount, date, time)
        )
        conn.commit()
        cursor.close()
        return_connection(conn)
    
    @staticmethod
    def get_by_name(user_id: int, name: str, limit: int = 10, offset: int = 0) -> List[Dict]:
        """Get history by goal name"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM goal_history WHERE user_id=%s AND name=%s ORDER BY id DESC LIMIT %s OFFSET %s",
            (user_id, name, limit, offset)
        )
        rows = cursor.fetchall()
        cursor.close()
        return_connection(conn)
        
        return [{'id': r[0], 'user_id': r[1], 'name': r[2], 'amount': r[3], 'date': r[4], 'time': r[5]} for r in rows]
    
    @staticmethod
    def delete_by_name(user_id: int, name: str):
        """Delete all history by goal name"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM goal_history WHERE user_id=%s AND name=%s",
            (user_id, name)
        )
        conn.commit()
        cursor.close()
        return_connection(conn)
    
    @staticmethod
    def delete_user_data(user_id: int):
        """Delete all user goal history"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM goal_history WHERE user_id=%s", (user_id,))
        conn.commit()
        cursor.close()
        return_connection(conn)


class UserRepository:
    """User data repository"""
    
    @staticmethod
    def get_language(user_id: int) -> str:
        """Get user language"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT lang FROM user_language WHERE user_id=%s",
            (user_id,)
        )
        row = cursor.fetchone()
        cursor.close()
        return_connection(conn)
        return row[0] if row else "bn"
    
    @staticmethod
    def set_language(user_id: int, lang: str):
        """Set user language"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO user_language (user_id, lang) VALUES (%s, %s) ON CONFLICT (user_id) DO UPDATE SET lang=%s",
            (user_id, lang, lang)
        )
        conn.commit()
        cursor.close()
        return_connection(conn)
