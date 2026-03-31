import json
from bot.database.connection import get_db_connection
from bot.config import Config
import logging

logger = logging.getLogger(__name__)

class BalanceRepository:
    @staticmethod
    def get_monthly_data(user_id, month):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM balance_data WHERE user_id=%s AND month=%s", (user_id, month))
            row = cursor.fetchone()
            
            if not row:
                default_wallets = json.dumps(Config.DEFAULT_WALLETS)
                cursor.execute(
                    "INSERT INTO balance_data (user_id, month, wallets, history) VALUES (%s, %s, %s, %s)",
                    (user_id, month, default_wallets, '[]')
                )
                conn.commit()
                cursor.execute("SELECT * FROM balance_data WHERE user_id=%s AND month=%s", (user_id, month))
                row = cursor.fetchone()
            
            data = {
                'user_id': row[0], 'month': row[1], 'total_income': row[2],
                'total_expense': row[3], 'budget_limit': row[4],
                'wallets': row[5] if isinstance(row[5], dict) else json.loads(row[5]),
                'history': row[6] if isinstance(row[6], list) else json.loads(row[6])
            }
            conn.commit()
            return data
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def update_monthly_data(user_id, month, data):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """UPDATE balance_data SET total_income=%s, total_expense=%s, budget_limit=%s, wallets=%s, history=%s 
                   WHERE user_id=%s AND month=%s""",
                (data['total_income'], data['total_expense'], data['budget_limit'],
                 json.dumps(data['wallets']), json.dumps(data['history']), user_id, month)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_all_months(user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM balance_data WHERE user_id=%s", (user_id,))
            rows = cursor.fetchall()
            all_data = []
            for row in rows:
                all_data.append({
                    'user_id': row[0], 'month': row[1], 'total_income': row[2],
                    'total_expense': row[3], 'budget_limit': row[4],
                    'wallets': row[5] if isinstance(row[5], dict) else json.loads(row[5]),
                    'history': row[6] if isinstance(row[6], list) else json.loads(row[6])
                })
            conn.commit()
            return all_data
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def delete_user_data(user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM balance_data WHERE user_id=%s", (user_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def delete_month_data(user_id, month):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            default_wallets = json.dumps(Config.DEFAULT_WALLETS)
            cursor.execute(
                "UPDATE balance_data SET total_income=0, total_expense=0, history='[]', wallets=%s WHERE user_id=%s AND month=%s",
                (default_wallets, user_id, month)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()


class DebtRepository:
    @staticmethod
    def get_all(user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM debt_data WHERE user_id=%s", (user_id,))
            rows = cursor.fetchall()
            conn.commit()
            return [{'id': r[0], 'user_id': r[1], 'name': r[2], 'type': r[3], 'amount': r[4]} for r in rows]
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_by_type(user_id, debt_type):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM debt_data WHERE user_id=%s AND type=%s", (user_id, debt_type))
            rows = cursor.fetchall()
            conn.commit()
            return [{'id': r[0], 'user_id': r[1], 'name': r[2], 'type': r[3], 'amount': r[4]} for r in rows]
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_distinct_names(user_id, debt_type):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT DISTINCT name FROM debt_data WHERE user_id=%s AND type=%s", (user_id, debt_type))
            names = [row[0] for row in cursor.fetchall()]
            conn.commit()
            return names
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def add_or_update(user_id, name, debt_type, amount):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM debt_data WHERE user_id=%s AND name=%s AND type=%s", (user_id, name, debt_type))
            row = cursor.fetchone()
            if row:
                cursor.execute("UPDATE debt_data SET amount = amount + %s WHERE id=%s", (amount, row[0]))
            else:
                cursor.execute("INSERT INTO debt_data (user_id, name, type, amount) VALUES (%s,%s,%s,%s)", (user_id, name, debt_type, amount))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def update_amount(debt_id, new_amount):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE debt_data SET amount=%s WHERE id=%s", (new_amount, debt_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_by_id(debt_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM debt_data WHERE id=%s", (debt_id,))
            row = cursor.fetchone()
            conn.commit()
            if row:
                return {'id': row[0], 'user_id': row[1], 'name': row[2], 'type': row[3], 'amount': row[4]}
            return None
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def delete_by_name(user_id, name):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM debt_data WHERE user_id=%s AND name=%s", (user_id, name))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def delete_user_data(user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM debt_data WHERE user_id=%s", (user_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()


class DebtHistoryRepository:
    @staticmethod
    def add(user_id, name, amount, date, time):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO debt_history (user_id, name, amount, date, time) VALUES (%s,%s,%s,%s,%s)",
                (user_id, name, amount, date, time)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_by_name(user_id, name, limit=10, offset=0):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT * FROM debt_history WHERE user_id=%s AND name=%s ORDER BY id DESC LIMIT %s OFFSET %s",
                (user_id, name, limit, offset)
            )
            rows = cursor.fetchall()
            cursor.execute("SELECT COUNT(*) FROM debt_history WHERE user_id=%s AND name=%s", (user_id, name))
            total = cursor.fetchone()[0]
            conn.commit()
            return [{'id': r[0], 'user_id': r[1], 'name': r[2], 'amount': r[3], 'date': r[4], 'time': r[5]} for r in rows], total
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def delete_by_name(user_id, name):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM debt_history WHERE user_id=%s AND name=%s", (user_id, name))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def delete_user_data(user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM debt_history WHERE user_id=%s", (user_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()


class OutstandingRepository:
    @staticmethod
    def get_all(user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM outstanding_data WHERE user_id=%s", (user_id,))
            rows = cursor.fetchall()
            conn.commit()
            return [{'id': r[0], 'user_id': r[1], 'name': r[2], 'type': r[3], 'amount': r[4]} for r in rows]
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_by_type(user_id, out_type):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM outstanding_data WHERE user_id=%s AND type=%s", (user_id, out_type))
            rows = cursor.fetchall()
            conn.commit()
            return [{'id': r[0], 'user_id': r[1], 'name': r[2], 'type': r[3], 'amount': r[4]} for r in rows]
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_distinct_names(user_id, out_type):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT DISTINCT name FROM outstanding_data WHERE user_id=%s AND type=%s", (user_id, out_type))
            names = [row[0] for row in cursor.fetchall()]
            conn.commit()
            return names
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def add_or_update(user_id, name, out_type, amount):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM outstanding_data WHERE user_id=%s AND name=%s AND type=%s", (user_id, name, out_type))
            row = cursor.fetchone()
            if row:
                cursor.execute("UPDATE outstanding_data SET amount = amount + %s WHERE id=%s", (amount, row[0]))
            else:
                cursor.execute("INSERT INTO outstanding_data (user_id, name, type, amount) VALUES (%s,%s,%s,%s)", (user_id, name, out_type, amount))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def update_amount(out_id, new_amount):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE outstanding_data SET amount=%s WHERE id=%s", (new_amount, out_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_by_id(out_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM outstanding_data WHERE id=%s", (out_id,))
            row = cursor.fetchone()
            conn.commit()
            if row:
                return {'id': row[0], 'user_id': row[1], 'name': row[2], 'type': row[3], 'amount': row[4]}
            return None
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def delete_by_name(user_id, name):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM outstanding_data WHERE user_id=%s AND name=%s", (user_id, name))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def delete_user_data(user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM outstanding_data WHERE user_id=%s", (user_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()


class OutstandingHistoryRepository:
    @staticmethod
    def add(user_id, name, amount, date, time):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO outstanding_history (user_id, name, amount, date, time) VALUES (%s,%s,%s,%s,%s)",
                (user_id, name, amount, date, time)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_by_name(user_id, name):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM outstanding_history WHERE user_id=%s AND name=%s ORDER BY id DESC", (user_id, name))
            rows = cursor.fetchall()
            conn.commit()
            return [{'id': r[0], 'user_id': r[1], 'name': r[2], 'amount': r[3], 'date': r[4], 'time': r[5]} for r in rows]
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def delete_by_name(user_id, name):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM outstanding_history WHERE user_id=%s AND name=%s", (user_id, name))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def delete_user_data(user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM outstanding_history WHERE user_id=%s", (user_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()


class GoalRepository:
    @staticmethod
    def get_all(user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM savings_goals WHERE user_id=%s", (user_id,))
            rows = cursor.fetchall()
            conn.commit()
            return [{'user_id': r[0], 'name': r[1], 'target': r[2], 'saved': r[3]} for r in rows]
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def add_or_update(user_id, name, target):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO savings_goals (user_id, name, target, saved) VALUES (%s, %s, %s, 0) ON CONFLICT (user_id, name) DO UPDATE SET target=%s",
                (user_id, name, target, target)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def add_savings(user_id, name, amount):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE savings_goals SET saved = saved + %s WHERE user_id=%s AND name=%s", (amount, user_id, name))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def delete_by_name(user_id, name):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM savings_goals WHERE user_id=%s AND name=%s", (user_id, name))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def delete_user_data(user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM savings_goals WHERE user_id=%s", (user_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()


class GoalHistoryRepository:
    @staticmethod
    def add(user_id, name, amount, date, time):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO goal_history (user_id, name, amount, date, time) VALUES (%s,%s,%s,%s,%s)",
                (user_id, name, amount, date, time)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_by_name(user_id, name, limit=10):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT * FROM goal_history WHERE user_id=%s AND name=%s ORDER BY id DESC LIMIT %s",
                (user_id, name, limit)
            )
            rows = cursor.fetchall()
            conn.commit()
            return [{'id': r[0], 'user_id': r[1], 'name': r[2], 'amount': r[3], 'date': r[4], 'time': r[5]} for r in rows]
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def delete_by_name(user_id, name):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM goal_history WHERE user_id=%s AND name=%s", (user_id, name))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def delete_user_data(user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM goal_history WHERE user_id=%s", (user_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()


class UserRepository:
    @staticmethod
    def get_language(user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT lang FROM user_language WHERE user_id=%s", (user_id,))
            row = cursor.fetchone()
            conn.commit()
            return row[0] if row else "bn"
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def set_language(user_id, lang):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO user_language (user_id, lang) VALUES (%s, %s) ON CONFLICT (user_id) DO UPDATE SET lang=%s",
                (user_id, lang, lang)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
