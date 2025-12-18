"""
Coordinator module that manages the authentication flow between hardware components.
"""
import threading
import time
from app.models.database import db
from app.hardware.printer import Printer

class AuthCoordinator:
    def __init__(self, socketio):
        """
        Initialize the authentication coordinator.
        
        Args:
            socketio: Flask-SocketIO instance for emitting events
        """
        self.socketio = socketio
        self.current_rfid = None
        self.pin_buffer = ""
        self.lock = threading.Lock()
        self.printer = Printer()
        
    def handle_rfid_detected(self, rfid_uid):
        """
        Handle when an RFID card is detected.
        
        Args:
            rfid_uid (str): The RFID UID of the detected card
        """
        with self.lock:
            self.current_rfid = rfid_uid
            self.pin_buffer = ""
            
        # Request PIN from user
        self.socketio.emit('request_pin', {'rfid_uid': rfid_uid})
        
    def handle_key_press(self, key):
        """
        Handle when a key is pressed on the keypad.
        
        Args:
            key (str): The pressed key
        """
        with self.lock:
            if self.current_rfid is None:
                return
                
            if key == '#':  # Enter key
                self._process_pin_entry()
            elif key == '*':  # Clear/backspace key
                if self.pin_buffer:
                    self.pin_buffer = self.pin_buffer[:-1]
            elif key.isdigit():
                self.pin_buffer += key
                
            # Send current PIN buffer to frontend
            self.socketio.emit('pin_updated', {
                'rfid_uid': self.current_rfid,
                'pin_length': len(self.pin_buffer)
            })
    
    def _process_pin_entry(self):
        """Process the entered PIN."""
        with self.lock:
            if not self.current_rfid or not self.pin_buffer:
                return
                
            rfid_uid = self.current_rfid
            pin = self.pin_buffer
            
            # Reset for next authentication
            self.current_rfid = None
            self.pin_buffer = ""
        
        # Authenticate user
        success = db.authenticate_user(rfid_uid, pin)
        
        # Log the authentication attempt
        message = "Access granted" if success else "Invalid PIN"
        db.log_event(rfid_uid, success, message)
        
        # Print receipt
        self.printer.print_receipt(rfid_uid, success, message)
        
        # Notify frontend of authentication result
        self.socketio.emit('auth_result', {
            'rfid_uid': rfid_uid,
            'success': success,
            'message': message
        })

# Global coordinator instance
auth_coordinator = None

def get_coordinator(socketio):
    """Get or create the global authentication coordinator."""
    global auth_coordinator
    if auth_coordinator is None:
        auth_coordinator = AuthCoordinator(socketio)
    return auth_coordinator