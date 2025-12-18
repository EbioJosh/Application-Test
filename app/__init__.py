"""
Main application entry point for the Raspberry Pi hardware appliance.
"""
import os
import sys
from flask import Flask, send_from_directory
from flask_socketio import SocketIO

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
    
    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # Register blueprints
    from app.api.routes import api_bp
    app.register_blueprint(api_bp)
    
    # Serve React frontend
    @app.route('/')
    def index():
        """Serve the React frontend."""
        static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
        return send_from_directory(static_folder, 'index.html')
    
    # Set up SocketIO event handlers
    @socketio.on('connect')
    def handle_connect():
        print('Client connected')
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')
    
    return app, socketio

if __name__ == '__main__':
    app, socketio = create_app()
    
    # Import hardware modules after app creation to avoid circular imports
    from app.hardware.rfid_reader import RFIDReader
    from app.hardware.keypad import Keypad
    from app.hardware.coordinator import get_coordinator
    
    # Get the authentication coordinator
    coordinator = get_coordinator(socketio)
    
    # Initialize hardware components
    rfid_reader = RFIDReader(socketio)
    keypad = Keypad(socketio)
    
    # Set up SocketIO event handlers for hardware events
    @socketio.on('rfid_detected')
    def handle_rfid(data):
        rfid_uid = data.get('rfid_uid')
        if rfid_uid:
            coordinator.handle_rfid_detected(rfid_uid)
    
    @socketio.on('key_pressed')
    def handle_key(data):
        key = data.get('key')
        if key:
            coordinator.handle_key_press(key)
    
    # Start hardware threads
    rfid_reader.start()
    keypad.start()
    
    # Run the Flask application
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False)