"""
Main application entry point for the Raspberry Pi hardware appliance.
"""
import os
import sys
import signal
from flask import Flask, send_from_directory
from flask_socketio import SocketIO
from flask import request
from flask_socketio import emit
from app.hardware.coordinator import get_coordinator

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

    # Handle balance inquiries from the frontend
    @socketio.on('balance_request')
    def handle_balance_request(data):
        # expected payload: { 'account_id': '1234' }
        account_id = data.get('account_id') if data else None
        coordinator = get_coordinator(socketio)

        # Simulated accounts (mirror of api routes)
        accounts = {
            '1234': {
                'name': 'John Doe',
                'accountNumber': '**** **** **** 1234',
                'balance': 1250.75,
                'cardUid': '1234'
            }
        }

        if not account_id or account_id not in accounts:
            emit('balance_response', {'error': 'Account not found'}, room=request.sid)
            return

        balance = accounts[account_id]['balance']
        # Print receipt for balance inquiry via hardware printer
        try:
            coordinator.printer.print_transaction_receipt(account_id, 'Balance Inquiry', 0.0, balance)
        except Exception:
            pass

        emit('balance_response', {'account_id': account_id, 'balance': balance}, room=request.sid)

    # Handle withdrawal requests from the frontend
    @socketio.on('withdraw')
    def handle_withdraw(data):
        # expected payload: { 'account_id': '1234', 'amount': 20.0 }
        account_id = data.get('account_id') if data else None
        amount = float(data.get('amount') or 0)
        coordinator = get_coordinator(socketio)

        # Simulated accounts (no persistence)
        accounts = {
            '1234': {
                'name': 'John Doe',
                'accountNumber': '**** **** **** 1234',
                'balance': 1250.75,
                'cardUid': '1234'
            }
        }

        if not account_id or account_id not in accounts:
            emit('transaction_result', {'success': False, 'message': 'Account not found'}, room=request.sid)
            return

        if amount <= 0:
            emit('transaction_result', {'success': False, 'message': 'Invalid amount'}, room=request.sid)
            return

        acct = accounts[account_id]
        new_balance = acct['balance'] - amount
        success = new_balance >= 0
        message = 'Transaction successful' if success else 'Insufficient funds'

        # Print transaction receipt
        try:
            coordinator.printer.print_transaction_receipt(account_id, 'Withdrawal', amount, new_balance if success else acct['balance'])
        except Exception:
            pass

        emit('transaction_result', {
            'success': success,
            'account_id': account_id,
            'amount': amount,
            'balance': new_balance if success else acct['balance'],
            'message': message
        }, room=request.sid)

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
