import sqlite3
import hashlib

class Database:
    def __init__(self, db_path='app.db'):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        """Creates a connection to the SQLite database with row factory enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initializes the database schema if it doesn't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Users Table (Authentication)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rfid_uid TEXT UNIQUE NOT NULL,
                pin_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Accounts Table (ATM Data)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rfid_uid TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                account_number TEXT NOT NULL,
                balance REAL NOT NULL DEFAULT 0
            )
        """)

        # Transaction History Table (For printable receipts and history)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rfid_uid TEXT,
                type TEXT, -- 'WITHDRAWAL' or 'BALANCE_INQUIRY'
                amount REAL,
                balance_after REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # General Logs Table (For security auditing)
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

    # ---------------- AUTH METHODS ----------------

    def add_user(self, rfid_uid, pin):
        """Hashes the pin and inserts the user into the database."""
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
        """Verifies if the provided PIN matches the hash in the database."""
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

    # ---------------- ACCOUNT METHODS ----------------

    def create_account(self, rfid_uid, name, account_number, balance):
        """Registers a new account tied to an RFID UID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO accounts (rfid_uid, name, account_number, balance)
            VALUES (?, ?, ?, ?)
        """, (rfid_uid, name, account_number, balance))
        conn.commit()
        conn.close()

    def get_account(self, rfid_uid):
        """Retrieves account details for a specific card."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM accounts WHERE rfid_uid=?",
            (rfid_uid,)
        )
        account = cursor.fetchone()
        conn.close()
        return dict(account) if account else None

    # ---------------- TRANSACTION METHODS ----------------

    def record_transaction(self, rfid_uid, tx_type, amount, balance_after):
        """Updates the account balance and logs the transaction record."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Update balance in accounts table
            cursor.execute(
                "UPDATE accounts SET balance=? WHERE rfid_uid=?",
                (balance_after, rfid_uid)
            )
            # Log specific transaction entry
            cursor.execute("""
                INSERT INTO transactions (rfid_uid, type, amount, balance_after)
                VALUES (?, ?, ?, ?)
            """, (rfid_uid, tx_type, amount, balance_after))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
        finally:
            conn.close()

    def log_event(self, rfid_uid, success, message):
        """Logs general access attempts (Success/Failure)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO logs (rfid_uid, success, message) VALUES (?, ?, ?)",
            (rfid_uid, success, message)
        )
        conn.commit()
        conn.close()

# Initialize singleton instance
db = Database()
