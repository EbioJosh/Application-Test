#!/bin/bash
# Raspberry Pi 4B Test Environment Setup Script

echo "==============================================="
echo "Raspberry Pi 4B Hardware Appliance Test Setup"
echo "==============================================="

# Update system packages
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
echo "Installing system dependencies..."
sudo apt install -y python3 python3-pip python3-venv git

# Create project directory
echo "Creating project directory..."
mkdir -p ~/rpi-hardware-test
cd ~/rpi-hardware-test

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv rpi-test-env
source rpi-test-env/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies (test environment - no hardware libraries)
echo "Installing Python dependencies for test environment..."
pip install Flask==2.3.3 Flask-SocketIO==5.3.6 python-escpos==3.1 python-socketio==5.8.0 eventlet==0.33.3

# Create a simple test database
echo "Creating test database..."
python3 -c "
import sqlite3
import hashlib

# Create database
conn = sqlite3.connect('app.db')
cursor = conn.cursor()

# Create users table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rfid_uid TEXT UNIQUE NOT NULL,
        pin_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Create logs table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rfid_uid TEXT,
        success BOOLEAN NOT NULL,
        message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Add a test user (PIN: 1234)
pin_hash = hashlib.sha256('1234'.encode()).hexdigest()
cursor.execute('''
    INSERT OR IGNORE INTO users (rfid_uid, pin_hash) 
    VALUES (?, ?)
''', ('123456789', pin_hash))

conn.commit()
conn.close()
print('Test database created with sample user (RFID: 123456789, PIN: 1234)')
"

# Create a simplified test application
echo "Creating test application..."
cat > test_app.py << 'EOF'
#!/usr/bin/env python3
"""
Simplified test application for Raspberry Pi 4B
This version simulates hardware for testing purposes
"""

import threading
import time
import random
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
import sqlite3
import hashlib

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Simulated hardware state
simulated_rfid_cards = ['123456789', '987654321', '456789123']
current_rfid = None
pin_buffer = ""

# Database functions
def get_db_connection():
    conn = sqlite3.connect('app.db')
    conn.row_factory = sqlite3.Row
    return conn

def authenticate_user(rfid_uid, pin):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    pin_hash = hashlib.sha256(pin.encode()).hexdigest()
    
    cursor.execute(
        'SELECT * FROM users WHERE rfid_uid = ? AND pin_hash = ?',
        (rfid_uid, pin_hash)
    )
    
    user = cursor.fetchone()
    conn.close()
    
    return user is not None

def log_event(rfid_uid, success, message):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT INTO logs (rfid_uid, success, message) VALUES (?, ?, ?)',
        (rfid_uid, success, message)
    )
    
    conn.commit()
    conn.close()

# Simulated hardware functions
def simulate_rfid_reading():
    """Simulate RFID card reading every 10-30 seconds"""
    while True:
        time.sleep(random.randint(10, 30))
        
        # Simulate detecting a card
        card_id = random.choice(simulated_rfid_cards)
        print(f"SIMULATED: RFID card detected: {card_id}")
        
        # Emit event
        socketio.emit('rfid_detected', {'rfid_uid': card_id})
        socketio.emit('request_pin', {'rfid_uid': card_id})

def simulate_keypad_input():
    """Simulate keypad input"""
    global current_rfid, pin_buffer
    
    while True:
        time.sleep(random.randint(5, 15))
        
        if current_rfid:
            # Simulate key presses
            keys = ['1', '2', '3', '4', '#']  # Simulate entering PIN 1234 and pressing #
            for key in keys:
                time.sleep(0.5)
                print(f"SIMULATED: Key pressed: {key}")
                socketio.emit('key_pressed', {'key': key})

# API Routes
@app.route('/')
def index():
    return jsonify({
        'message': 'Raspberry Pi 4B Hardware Appliance - Test Environment',
        'status': 'running',
        'hardware_simulation': 'active'
    })

@app.route('/api/status')
def get_status():
    return jsonify({
        'status': 'online',
        'message': 'System is running in test mode',
        'hardware_simulation': 'active'
    })

@app.route('/api/users', methods=['POST'])
def add_user():
    data = request.get_json()
    
    if not data or 'rfid_uid' not in data or 'pin' not in data:
        return jsonify({'error': 'Missing rfid_uid or pin'}), 400
    
    rfid_uid = data['rfid_uid']
    pin = data['pin']
    
    if len(pin) < 4:
        return jsonify({'error': 'PIN must be at least 4 characters'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    pin_hash = hashlib.sha256(pin.encode()).hexdigest()
    
    try:
        cursor.execute(
            'INSERT INTO users (rfid_uid, pin_hash) VALUES (?, ?)',
            (rfid_uid, pin_hash)
        )
        conn.commit()
        result = True
    except sqlite3.IntegrityError:
        result = False
    finally:
        conn.close()
    
    if result:
        return jsonify({'message': 'User added successfully'}), 201
    else:
        return jsonify({'error': 'RFID UID already exists'}), 409

@app.route('/api/logs')
def get_logs():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM logs ORDER BY created_at DESC LIMIT 20')
    logs = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify(logs)

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    print('Client connected to test environment')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected from test environment')

@socketio.on('rfid_detected')
def handle_rfid(data):
    global current_rfid
    rfid_uid = data.get('rfid_uid')
    if rfid_uid:
        current_rfid = rfid_uid
        print(f"Test system: Processing RFID {rfid_uid}")

@socketio.on('key_pressed')
def handle_key(data):
    global current_rfid, pin_buffer
    
    key = data.get('key')
    if not key or not current_rfid:
        return
        
    if key == '#':  # Enter key
        # Process PIN
        if pin_buffer:
            success = authenticate_user(current_rfid, pin_buffer)
            message = "Access granted" if success else "Invalid PIN"
            
            # Log the event
            log_event(current_rfid, success, message)
            
            # Emit result
            socketio.emit('auth_result', {
                'rfid_uid': current_rfid,
                'success': success,
                'message': message
            })
            
            print(f"AUTH RESULT: {message} for card {current_rfid}")
            
        # Reset for next authentication
        current_rfid = None
        pin_buffer = ""
        
    elif key == '*':  # Clear/backspace key
        if pin_buffer:
            pin_buffer = pin_buffer[:-1]
    elif key.isdigit():
        pin_buffer += key
        
        # Send PIN update
        socketio.emit('pin_updated', {
            'rfid_uid': current_rfid,
            'pin_length': len(pin_buffer)
        })

if __name__ == '__main__':
    print("Starting Raspberry Pi 4B Hardware Appliance Test Environment...")
    print("===============================================")
    print("Features:")
    print("- Simulated RFID card reading")
    print("- Simulated keypad input")
    print("- Authentication against SQLite database")
    print("- WebSocket event emission")
    print("- REST API endpoints")
    print("===============================================")
    print("Starting hardware simulation threads...")
    
    # Start simulation threads
    rfid_thread = threading.Thread(target=simulate_rfid_reading, daemon=True)
    keypad_thread = threading.Thread(target=simulate_keypad_input, daemon=True)
    
    rfid_thread.start()
    keypad_thread.start()
    
    print("Hardware simulation threads started")
    print("Starting Flask server...")
    print("Access the application at: http://localhost:5000")
    
    # Run the Flask application
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False)
EOF

# Make the test application executable
chmod +x test_app.py

# Create a simple test script
echo "Creating test script..."
cat > run_test.sh << 'EOF'
#!/bin/bash
source rpi-test-env/bin/activate
python test_app.py
EOF

chmod +x run_test.sh

# Create systemd service file for test environment
echo "Creating systemd service file..."
cat > rpi-hardware-test.service << 'EOF'
[Unit]
Description=Raspberry Pi 4B Hardware Appliance Test Environment
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/rpi-hardware-test
ExecStart=/home/pi/rpi-hardware-test/rpi-test-env/bin/python test_app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "==============================================="
echo "Raspberry Pi 4B Test Environment Setup Complete!"
echo "==============================================="
echo "To run the application:"
echo "1. Activate environment: source rpi-test-env/bin/activate"
echo "2. Run manually: python test_app.py"
echo "3. Or use helper script: ./run_test.sh"
echo ""
echo "To install as systemd service:"
echo "sudo cp rpi-hardware-test.service /etc/systemd/system/"
echo "sudo systemctl daemon-reload"
echo "sudo systemctl enable rpi-hardware-test"
echo "sudo systemctl start rpi-hardware-test"
echo ""
echo "Test user credentials:"
echo "- RFID UID: 123456789"
echo "- PIN: 1234"
echo ""
echo "API endpoints:"
echo "- Status: http://localhost:5000/api/status"
echo "- Logs: http://localhost:5000/api/logs"
echo "- Add user: POST to http://localhost:5000/api/users"
echo ""
echo "WebSocket events:"
echo "- rfid_detected: When RFID card is detected"
echo "- request_pin: When PIN entry is requested"
echo "- key_pressed: When keypad key is pressed"
echo "- pin_updated: When PIN buffer changes"
echo "- auth_result: When authentication completes"