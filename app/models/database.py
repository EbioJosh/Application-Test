"""
Database models for the Raspberry Pi hardware appliance.
"""
import sqlite3
import hashlib
import os

class Database:
    def __init__(self, db_path='app.db'):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize the database with required tables."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create users table for RFID UIDs and PINs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rfid_uid TEXT UNIQUE NOT NULL,
                pin_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create logs table for authentication events
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rfid_uid TEXT,
                success BOOLEAN NOT NULL,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, rfid_uid, pin):
        """Add a new user with RFID UID and PIN."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Hash the PIN for security
        pin_hash = hashlib.sha256(pin.encode()).hexdigest()
        
        try:
            cursor.execute(
                'INSERT INTO users (rfid_uid, pin_hash) VALUES (?, ?)',
                (rfid_uid, pin_hash)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # RFID UID already exists
            return False
        finally:
            conn.close()
    
    def authenticate_user(self, rfid_uid, pin):
        """Authenticate a user with RFID UID and PIN."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Hash the PIN for comparison
        pin_hash = hashlib.sha256(pin.encode()).hexdigest()
        
        cursor.execute(
            'SELECT * FROM users WHERE rfid_uid = ? AND pin_hash = ?',
            (rfid_uid, pin_hash)
        )
        
        user = cursor.fetchone()
        conn.close()
        
        return user is not None
    
    def log_event(self, rfid_uid, success, message):
        """Log an authentication event."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO logs (rfid_uid, success, message) VALUES (?, ?, ?)',
            (rfid_uid, success, message)
        )
        
        conn.commit()
        conn.close()

# Global database instance
db = Database()