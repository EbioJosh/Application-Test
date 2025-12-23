"""
Main application entry point for the Raspberry Pi hardware appliance.
"""
import os
import sys
import signal
from flask import Flask, send_from_directory
from flask_socketio import SocketIO

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    app.config['SECRET_KEY'] = 'change-this-in-production'

    socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

    # Register API routes
    from app.api.routes import api_bp
    app.register_blueprint(api_bp)

    # Serve React frontend
    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')

    @socketio.on('connect')
    def handle_connect():
        print('UI connected')

    @socketio.on('disconnect')
    def handle_disconnect():
        print('UI disconnected')

    return app, socketio

# =========================================================
# Application startup
# =========================================================
if __name__ == '__main__':
    app, socketio = create_app()

    # Import hardware AFTER SocketIO creation
    from app.hardware.rfid_reader import RFIDReader
    from app.hardware.keypad import Keypad
    from app.hardware.coordinator import get_coordinator

    # Coordinator controls authentication flow
    coordinator = get_coordinator(socketio)

    # Initialize hardware components
    rfid_reader = RFIDReader(coordinator)
    keypad = Keypad(coordinator)

    # Coordinator holds references to hardware
    coordinator.set_hardware_components(rfid_reader, keypad)

    # Start hardware threads
    rfid_reader.start()
    keypad.start()

    # Graceful shutdown
    def shutdown(sig, frame):
        print("Shutting down...")
        rfid_reader.stop()
        keypad.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    print("Raspberry Pi Banking Appliance running on port 5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False)
