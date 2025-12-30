import threading
import time
from app.models.database import db
from app.hardware.printer import Printer

class AuthCoordinator:
    def __init__(self, socketio):
        self.socketio = socketio
        self.current_rfid = None
        self.pin_buffer = ""
        self.amount_buffer = ""
        
        # States: IDLE, PIN_ENTRY, AUTHENTICATED, WITHDRAWING
        self.state = "IDLE" 
        
        self.lock = threading.Lock()
        self.printer = Printer()
        
        # Hardware references (Linked via set_hardware_components)
        self.rfid_reader = None
        self.keypad = None

        # Timeout Monitoring (30 Seconds)
        self.last_activity_time = time.time()
        self.timeout_duration = 30
        self.timer_thread = threading.Thread(target=self._timeout_monitor, daemon=True)
        self.timer_thread.start()

    def set_hardware_components(self, rfid_reader, keypad):
        """
        Fixes the AttributeError. This method allows run.py 
        to pass the hardware instances to the coordinator.
        """
        self.rfid_reader = rfid_reader
        self.keypad = keypad

    def reset_timer(self):
        """Resets the inactivity clock whenever a user interacts."""
        self.last_activity_time = time.time()

    def _timeout_monitor(self):
        """Background thread that resets the session after 30s of silence."""
        while True:
            if self.state != "IDLE":
                if time.time() - self.last_activity_time > self.timeout_duration:
                    print("[TIMEOUT] 30s passed. Resetting to IDLE.")
                    self.reset_session()
            time.sleep(1)

    def handle_rfid_detected(self, rfid_uid):
        self.reset_timer()
        with self.lock:
            # STRICT CHECK: Only allow transition if we are truly IDLE
            if self.state != "IDLE":
                print(f"[COORDINATOR] Blocked RFID read: System is in state {self.state}")
                return
                
            self.current_rfid = rfid_uid
            self.state = "PIN_ENTRY"
            self.pin_buffer = ""

        print(f"[COORDINATOR] RFID Accepted. Moving to PIN_ENTRY.")
        self.socketio.emit("request_pin", {"rfid_uid": rfid_uid})

    def reset_session(self):
        """Forces the system back to the 'Insert Card' screen safely."""
        with self.lock:
            # If we are already IDLE, don't do anything
            if self.state == "IDLE":
                return
                
            print("[COORDINATOR] Resetting Session to IDLE")
            self.state = "IDLE"
            self.current_rfid = None
            self.pin_buffer = ""
            self.amount_buffer = ""
            
        self.socketio.emit("session_timeout", {"message": "Session Ended"})

    # =========================
    # KEYPAD CALLBACK
    # =========================
    def handle_key_press(self, key):
        self.reset_timer()
        with self.lock:
            if self.state == "PIN_ENTRY":
                self._handle_pin_keypad(key)
            elif self.state == "WITHDRAWING":
                self._handle_withdrawal_keypad(key)

    def _handle_pin_keypad(self, key):
        if key == "6":  # Submit PIN
            self._process_pin_entry()
        elif key == "*":  # Backspace
            self.pin_buffer = self.pin_buffer[:-1]
        elif key.isdigit():
            self.pin_buffer += key
        
        self.socketio.emit("pin_updated", {
            "rfid_uid": self.current_rfid,
            "pin_length": len(self.pin_buffer)
        })

    def _handle_withdrawal_keypad(self, key):
        if key == "6":  # Confirm Amount
            # Tell the frontend to trigger the 'withdraw' event with this buffer
            self.socketio.emit("submit_withdrawal_amount", {"amount": self.amount_buffer})
            self.amount_buffer = ""
        elif key == "*":  # Backspace
            self.amount_buffer = self.amount_buffer[:-1]
        elif key.isdigit():
            self.amount_buffer += key
        
        # Show the amount typing on the screen in real-time
        self.socketio.emit("amount_updated", {"amount": self.amount_buffer})

    # =========================
    # LOGIC PROCESSING
    # =========================
    def _process_pin_entry(self):
        rfid_uid = self.current_rfid
        pin = self.pin_buffer

        success = db.authenticate_user(rfid_uid, pin)
        
        if success:
            self.state = "AUTHENTICATED"
            account = db.get_account(rfid_uid)
            message = "Access granted"
        else:
            self.state = "IDLE"
            self.current_rfid = None
            account = None
            message = "Invalid PIN"

        db.log_event(rfid_uid, success, message)
        self.socketio.emit("auth_result", {
            "success": success,
            "account": account,
            "message": message
        })

    def set_state(self, new_state):
        """Used by the Frontend to tell the Coordinator what the user is doing."""
        with self.lock:
            self.state = new_state
            if new_state == "WITHDRAWING":
                self.amount_buffer = ""

# =========================
# SINGLETON ACCESSOR
# =========================
_auth_coordinator = None

def get_coordinator(socketio):
    global _auth_coordinator
    if _auth_coordinator is None:
        _auth_coordinator = AuthCoordinator(socketio)
    return _auth_coordinator
