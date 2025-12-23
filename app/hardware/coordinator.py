import threading
from app.models.database import db
from app.hardware.printer import Printer

class AuthCoordinator:
    def __init__(self, socketio):
        self.socketio = socketio
        self.current_rfid = None
        self.pin_buffer = ""
        self.lock = threading.Lock()
        self.printer = Printer()
        self.rfid_reader = None
        self.keypad = None

    def set_hardware_components(self, rfid_reader, keypad):
        self.rfid_reader = rfid_reader
        self.keypad = keypad

    # Called when an RFID is detected
    def handle_rfid_detected(self, rfid_uid):
        with self.lock:
            self.current_rfid = rfid_uid
            self.pin_buffer = ""

        # Request PIN on frontend
        self.socketio.emit(
            'request_pin',
            {'rfid_uid': rfid_uid},
            broadcast=True
        )

    # Called when a key is pressed on keypad
    def handle_key_press(self, key):
        with self.lock:
            if self.current_rfid is None:
                return

            if key == '#':  # Submit PIN
                self._process_pin_entry()
                return
            elif key == '*':  # Backspace
                self.pin_buffer = self.pin_buffer[:-1]
            elif key.isdigit():
                self.pin_buffer += key


            # Emit PIN length AND actual buffer to frontend
            self.socketio.emit(
                'pin_updated',
                {
                    'rfid_uid': self.current_rfid,
                    'pin_length': len(self.pin_buffer),
                    'pin_buffer': self.pin_buffer
                },
		namespace='/',
                broadcast=True
            )

    def _process_pin_entry(self):
        rfid_uid = self.current_rfid
        pin = self.pin_buffer

        # Reset session
        self.current_rfid = None
        self.pin_buffer = ""

        # Authenticate user
        success = db.authenticate_user(rfid_uid, pin)
        message = "Access granted" if success else "Invalid PIN"

        # Log and print receipt
        db.log_event(rfid_uid, success, message)
        self.printer.print_receipt(rfid_uid, success, message)

        # Notify frontend of result
        self.socketio.emit(
            'auth_result',
            {'rfid_uid': rfid_uid, 'success': success, 'message': message},
            broadcast=True
        )

# Singleton pattern
auth_coordinator = None

def get_coordinator(socketio):
    global auth_coordinator
    if auth_coordinator is None:
        auth_coordinator = AuthCoordinator(socketio)
    return auth_coordinator
