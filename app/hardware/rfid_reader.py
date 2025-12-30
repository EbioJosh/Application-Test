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
        self.last_read_uid = None
        self.last_read_time = 0

        if GPIO.getmode() != GPIO.BCM:
            GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        try:
            self.reader = SimpleMFRC522()
            print("RFID Reader initialized.")
        except Exception as e:
            print(f"[RFID ERROR] Init failed: {e}")
            self.reader = None

    def start(self):
        if self.reader and not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._read_rfid_loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def _read_rfid_loop(self):
        while self.running:
            try:
                # read_no_block returns (uid, text)
                uid, _ = self.reader.read_no_block()

                if uid:
                    uid = str(uid)
                    current_time = time.time()

                    # 1. Logic: Only trigger if the system is IDLE
                    # 2. Logic: Ignore the SAME card for 5 seconds after a session ends
                    # to give the user time to remove it.
                    if self.coordinator.state == "IDLE":
                        if uid != self.last_read_uid or (current_time - self.last_read_time > 5):
                            print(f"RFID card detected: {uid}")
                            self.last_read_uid = uid
                            self.last_read_time = current_time
                            self.coordinator.handle_rfid_detected(uid)
                else:
                    # If no card is present, clear the last_read_uid 
                    # so the same card can be used again immediately once removed
                    self.last_read_uid = None

                time.sleep(0.5) # Reduced polling to prevent CPU spikes

            except Exception as e:
                print(f"[RFID ERROR] {e}")
                time.sleep(1)
