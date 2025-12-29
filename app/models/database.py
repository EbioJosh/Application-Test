import sqlite3
import hashlib

class Database:
    def __init__(self, db_path='app.db'):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Users (auth)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rfid_uid TEXT UNIQUE NOT NULL,
                pin_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Accounts (ATM data)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rfid_uid TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                account_number TEXT NOT NULL,
                balance REAL NOT NULL DEFAULT 0
            )
        """)

        # Logs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rfid_uid TEXT,
                success BOOLEAN,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    # ---------------- AUTH ----------------
    def add_user(self, rfid_uid, pin):
        pin_hash = hashlib.sha256(pin.encode()).hexdigest()
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO users (rfid_uid, pin_hash) VALUES (?, ?)",
            (rfid_uid, pin_hash)
        )
        conn.commit()
        conn.close()

    def authenticate_user(self, rfid_uid, pin):
        pin_hash = hashlib.sha256(pin.encode()).hexdigest()
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM users WHERE rfid_uid=? AND pin_hash=?",
            (rfid_uid, pin_hash)
        )
        result = cursor.fetchone()
        conn.close()
        return result is not None

    # ---------------- ACCOUNT ----------------
    def create_account(self, rfid_uid, name, account_number, balance):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO accounts (rfid_uid, name, account_number, balance)
            VALUES (?, ?, ?, ?)
        """, (rfid_uid, name, account_number, balance))
        conn.commit()
        conn.close()

    def get_account(self, rfid_uid):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM accounts WHERE rfid_uid=?",
            (rfid_uid,)
        )
        account = cursor.fetchone()
        conn.close()
        return dict(account) if account else None

    def update_balance(self, rfid_uid, new_balance):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE accounts SET balance=? WHERE rfid_uid=?",
            (new_balance, rfid_uid)
        )
        conn.commit()
        conn.close()

    def log_event(self, rfid_uid, success, message):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO logs (rfid_uid, success, message) VALUES (?, ?, ?)",
            (rfid_uid, success, message)
        )
        conn.commit()
        conn.close()


db = Database()
