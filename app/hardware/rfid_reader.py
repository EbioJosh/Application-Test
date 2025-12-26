"""
RFID Reader module for the Raspberry Pi hardware appliance.
"""

import threading
import time
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522


class RFIDReader:
    def __init__(self, coordinator):
        # ?? THIS is where your snippet goes
        self.coordinator = coordinator
        self.running = False
        self.thread = None

        # Ensure BCM mode (same as keypad)
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
            self.thread = threading.Thread(
                target=self._read_rfid_loop,
                daemon=True
            )
            self.thread.start()
            print("RFID Reader thread started.")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def _read_rfid_loop(self):
        while self.running:
            try:
                uid, _ = self.reader.read_no_block()

                if uid:
                    uid = str(uid)

                    # ?? Block re-reads while PIN is active
                    if self.coordinator.current_rfid is None:
                        print(f"RFID card read: {uid}")
                        self.coordinator.handle_rfid_detected(uid)

                    time.sleep(2)  # debounce

                time.sleep(0.1)

            except Exception as e:
                print(f"[RFID ERROR] {e}")
                time.sleep(1)
