"""
RFID Reader module for the Raspberry Pi hardware appliance.
"""
import threading
import time
import queue
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from config import Config

class RFIDReader:
    def __init__(self, socketio):
        """
        Initialize the RFID reader using BCM mode to match the keypad.
        """
        self.socketio = socketio
        
        # 1. Force BCM mode BEFORE initializing the reader
        # This prevents the "Channel invalid" error when mixing with Keypad
        current_mode = GPIO.getmode()
        if current_mode != GPIO.BCM:
            GPIO.setmode(GPIO.BCM)
        
        GPIO.setwarnings(False)
        
        # 2. Initialize the reader
        # Note: SimpleMFRC522 uses default SPI pins, but we ensure mode consistency
        try:
            self.reader = SimpleMFRC522()
        except Exception as e:
            print(f"Hardware Error: Could not initialize MFRC522. {e}")
            self.reader = None

        self.running = False 
        self.thread = None
        
    def start(self):
        """Start the RFID reading thread."""
        if not self.running and self.reader:
            self.running = True
            self.thread = threading.Thread(target=self._read_rfid_loop, daemon=True)
            self.thread.start()
            print("RFID Reader thread started.")
            
    def stop(self):
        """Stop the RFID reading thread."""
        self.running = False
        if self.thread:
            self.thread.join()
            
    def _read_rfid_loop(self):
        """Background thread function to continuously read RFID cards."""
        while self.running:
            try:
                # read_no_block returns (None, None) if no card is present
                id, text = self.reader.read_no_block()
                
                if id:
                    self._handle_rfid_read(str(id))
                    # Prevent multiple reads of the same card in a split second
                    time.sleep(2)
                
                time.sleep(0.1) # Short sleep to prevent CPU spiking
                    
            except Exception as e:
                print(f"Error reading RFID: {e}")
                time.sleep(1)
                
    def _handle_rfid_read(self, rfid_uid):
        """Handle when an RFID card is read."""
        print(f"RFID card read: {rfid_uid}")
        
        # Emit event to frontend via WebSocket
        self.socketio.emit('rfid_detected', {'rfid_uid': rfid_uid})
        
        # Notify the system that we need a PIN
        self.socketio.emit('request_pin', {'rfid_uid': rfid_uid})

        # Database logging should be handled via a callback or event to keep this clean
        # but for now, we follow your provided logic.
