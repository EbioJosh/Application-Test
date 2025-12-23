"""
Keypad module for Raspberry Pi
"""
import threading
import time
import queue
import RPi.GPIO as GPIO
from config import Config

class Keypad:
    def __init__(self, coordinator):
        self.coordinator = coordinator  # Must be AuthCoordinator instance
        self.running = False
        self.thread = None
        self.key_queue = queue.Queue()

        # GPIO pins from config
        self.rows = Config.KEYPAD_ROW_PINS
        self.cols = Config.KEYPAD_COL_PINS

        # 4x3 matrix
        self.key_map = [
            ["1", "2", "3"],
            ["4", "5", "6"],
            ["7", "8", "9"],
            ["*", "0", "#"]
        ]

        self._setup_gpio()

    def _setup_gpio(self):
        if GPIO.getmode() is None:
            GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        for pin in self.rows:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)

        for pin in self.cols:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._scan_keypad_loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        GPIO.cleanup()

    def _scan_keypad_loop(self):
        last_key = None
        debounce_time = 0.2

        while self.running:
            key_pressed = None
            for row_idx, row_pin in enumerate(self.rows):
                GPIO.output(row_pin, GPIO.HIGH)
                for col_idx, col_pin in enumerate(self.cols):
                    if GPIO.input(col_pin) == GPIO.HIGH:
                        key_pressed = self.key_map[row_idx][col_idx]
                GPIO.output(row_pin, GPIO.LOW)

            if key_pressed and key_pressed != last_key:
                self._handle_key_press(key_pressed)
                last_key = key_pressed
                time.sleep(debounce_time)
            elif not key_pressed:
                last_key = None

            # Simulated key presses
            if not self.key_queue.empty():
                sim_key = self.key_queue.get()
                self._handle_key_press(sim_key)

            time.sleep(0.05)

    def _handle_key_press(self, key):
        print(f"[KEYPAD] Key pressed: {key}")
        self.coordinator.handle_key_press(key)

    def simulate_key_press(self, key):
        self.key_queue.put(key)
