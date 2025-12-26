"""
Keypad diagnostic script

Usage:
  python tools/keypad_diag.py

Press keypad buttons while this runs. It will print the BCM pin for the row and column
that detected the press and the corresponding key label from the keypad `key_map`.

The script imports `Config` from `app.config` to use the same pin defaults as the application.
"""
import os
import sys
import time
import signal

# allow running from repo root
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from app.config import Config
except Exception:
    # fallback defaults if import fails
    class Config:
        KEYPAD_ROW_PINS = [5, 6, 13, 19]
        KEYPAD_COL_PINS = [12, 16, 20]

import RPi.GPIO as GPIO

ROWS = Config.KEYPAD_ROW_PINS
COLS = Config.KEYPAD_COL_PINS
KEY_MAP = [
    ["1", "2", "3"],
    ["4", "5", "6"],
    ["7", "8", "9"],
    ["*", "0", "#"]
]

# Common BCM -> physical header map for 40-pin Pi (useful but model-dependent)
BCM_TO_PHYSICAL = {
    2: 3, 3: 5, 4: 7, 14: 8, 15: 10, 17: 11, 18: 12, 27: 13,
    22: 15, 23: 16, 24: 18, 10: 19, 9: 21, 25: 22, 11: 23, 8: 24,
    7: 26, 5: 29, 6: 31, 12: 32, 13: 33, 19: 35, 16: 36, 26: 37,
    20: 38, 21: 40
}

def phys(pin):
    return BCM_TO_PHYSICAL.get(pin, '?')

def cleanup_and_exit(signum=None, frame=None):
    GPIO.cleanup()
    print('\nExiting, GPIO cleaned up.')
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, cleanup_and_exit)
    signal.signal(signal.SIGTERM, cleanup_and_exit)

    print('Keypad diagnostic starting. Rows (BCM):', ROWS, 'Cols (BCM):', COLS)
    print('Press keys on the keypad. Ctrl-C to exit.')

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    for r in ROWS:
        GPIO.setup(r, GPIO.OUT)
        GPIO.output(r, GPIO.LOW)

    for c in COLS:
        GPIO.setup(c, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    last_report = 0
    try:
        while True:
            detected = []
            for row_idx, r in enumerate(ROWS):
                GPIO.output(r, GPIO.HIGH)
                # small settle
                time.sleep(0.005)
                for col_idx, c in enumerate(COLS):
                    if GPIO.input(c) == GPIO.HIGH:
                        key = None
                        try:
                            key = KEY_MAP[row_idx][col_idx]
                        except Exception:
                            key = '?'
                        detected.append((r, phys(r), c, phys(c), key, row_idx, col_idx))
                GPIO.output(r, GPIO.LOW)

            now = time.time()
            if detected and now - last_report > 0.05:
                for r_bcm, r_phys, c_bcm, c_phys, key, ri, ci in detected:
                    print(f"Detected key: {key}  (row BCM {r_bcm} -> phys {r_phys}, col BCM {c_bcm} -> phys {c_phys})")
                last_report = now

            time.sleep(0.02)

    finally:
        cleanup_and_exit()

if __name__ == '__main__':
    main()
