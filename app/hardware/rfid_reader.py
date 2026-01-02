"""
REVISED RFID Reader module
"""
import threading
import time
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

class RFIDReader:
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.running = False
        self.thread = None
        self.last_uid = None  # Track the card currently/previously in the reader

        if GPIO.getmode() != GPIO.BCM:
            GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.reader = SimpleMFRC522()

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._read_rfid_loop, daemon=True)
            self.thread.start()

    def _read_rfid_loop(self):
        while self.running:
            try:
                uid, _ = self.reader.read_no_block()
                
                if uid:
                    uid = str(uid)
                    self.coordinator.socketio.emit("card_status", {"present": True, "uid": uid})
                    
                    # Only trigger a new login if system is IDLE and it's NOT the same card just used
                    if self.coordinator.state == "IDLE" and uid != self.last_uid:
                        self.last_uid = uid
                        self.coordinator.handle_rfid_detected(uid)
                else:
                    self.coordinator.socketio.emit("card_status", {"present": False})
                    # If no card is detected, clear the last_uid memory
                    # This allows the same card to be used again after it was removed
                    self.last_uid = None

                time.sleep(1) # Check every second for better responsiveness
            except Exception as e:
                print(f"RFID Error: {e}")
                time.sleep(1)
