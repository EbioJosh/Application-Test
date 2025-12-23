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
    RFID_SDA_PIN = int(os.environ.get('RFID_SDA_PIN', 8))
    RFID_SCK_PIN = int(os.environ.get('RFID_SCK_PIN', 11))
    RFID_MOSI_PIN = int(os.environ.get('RFID_MOSI_PIN', 10))
    RFID_MISO_PIN = int(os.environ.get('RFID_MISO_PIN', 9))
    RFID_RST_PIN = int(os.environ.get('RFID_RST_PIN', 25))
    
    # Keypad configuration
    # These read from environment variables or default to your provided list
    KEYPAD_ROW_PINS = [int(x) for x in os.environ.get('KEYPAD_ROW_PINS', '5,6,13,19').split(',') if x]
    KEYPAD_COL_PINS = [int(x) for x in os.environ.get('KEYPAD_COL_PINS', '12,16,20').split(',') if x]
