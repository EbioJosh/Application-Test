"""
Configuration settings for the Raspberry Pi hardware appliance.
"""

import os

class Config:
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database
    DATABASE_PATH = os.environ.get('DATABASE_PATH') or 'app.db'
    
    # Hardware settings
    RFID_READER_ENABLED = os.environ.get('RFID_READER_ENABLED', 'true').lower() == 'true'
    KEYPAD_ENABLED = os.environ.get('KEYPAD_ENABLED', 'true').lower() == 'true'
    PRINTER_ENABLED = os.environ.get('PRINTER_ENABLED', 'true').lower() == 'true'
    
    # GPIO pins (for Raspberry Pi)
    # These would be configured based on your specific hardware setup
    RFID_SDA_PIN = int(os.environ.get('RFID_SDA_PIN', 0))
    RFID_SCK_PIN = int(os.environ.get('RFID_SCK_PIN', 0))
    RFID_MOSI_PIN = int(os.environ.get('RFID_MOSI_PIN', 0))
    RFID_MISO_PIN = int(os.environ.get('RFID_MISO_PIN', 0))
    RFID_RST_PIN = int(os.environ.get('RFID_RST_PIN', 0))
    
    # Keypad configuration would go here
    # KEYPAD_ROW_PINS = [int(x) for x in os.environ.get('KEYPAD_ROW_PINS', '').split(',') if x]
    # KEYPAD_COL_PINS = [int(x) for x in os.environ.get('KEYPAD_COL_PINS', '').split(',') if x]