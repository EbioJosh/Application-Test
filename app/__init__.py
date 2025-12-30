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

from app.models.database import db

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    app.config['SECRET_KEY'] = 'atm-secret'
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

    from app.hardware.coordinator import get_coordinator
    from app.models.database import db

    @socketio.on('set_state')
    def handle_state_change(data):
        coord = get_coordinator(socketio)
        coord.set_state(data.get('state'))
        coord.reset_timer()

    @socketio.on('balance_request')
    def handle_balance_request(data):
        coord = get_coordinator(socketio)
        coord.reset_timer()
        rfid_uid = data.get('rfid_uid')
        account = db.get_account(rfid_uid)

        if account:
            db.record_transaction(rfid_uid, "BALANCE_INQUIRY", 0, account['balance'])
            emit('balance_response', {
                'name': account['name'],
                'account_number': account['account_number'],
                'balance': account['balance']
            })

    @socketio.on('withdraw')
    def handle_withdraw(data):
        coord = get_coordinator(socketio)
        coord.reset_timer()
        
        rfid_uid = data.get('rfid_uid')
        try:
            amount = float(data.get('amount', 0))
        except:
            emit('transaction_result', {'success': False, 'message': 'Invalid amount'})
            return

        # 1. Rule: Multiple of 500
        if amount <= 0 or amount % 500 != 0:
            emit('transaction_result', {'success': False, 'message': 'Please enter a multiple of ₱500'})
            return

        account = db.get_account(rfid_uid)
        if not account:
            emit('transaction_result', {'success': False, 'message': 'Account error'})
            return

        # 2. Rule: Enough balance
        if account['balance'] < amount:
            emit('transaction_result', {'success': False, 'message': 'Insufficient funds'})
            return

        # Success path
        new_balance = account['balance'] - amount
        db.record_transaction(rfid_uid, "WITHDRAWAL", amount, new_balance)

        emit('transaction_result', {
            'success': True,
            'amount': amount,
            'remaining_balance': new_balance,
            'message': 'Withdrawal successful. Please take your cash.'
        })

    @socketio.on('print_receipt')
    def handle_print(data):
        coord = get_coordinator(socketio)
        coord.printer.print_transaction_receipt(
            rfid_uid=data.get('rfid_uid'),
            title=data.get('title', 'ATM TRANSACTION'),
            amount=float(data.get('amount', 0)),
            remaining_balance=float(data.get('remaining_balance', 0))
        )
        emit('print_result', {'success': True})

    @socketio.on('done')
    def handle_done():
        coord = get_coordinator(socketio)
        coord.reset_session()

    return app, socketio
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
        rfid_uid = data.get('account_id')
        account = db.get_account(rfid_uid)

        if not account:
            emit('balance_response', {'error': 'Account not found'}, room=request.sid)
            return

        emit('balance_response', {
            'balance': account['balance']
        }, room=request.sid)

    # Handle withdrawal requests from the frontend
    @socketio.on('withdraw')
    def handle_withdraw(data):
        rfid_uid = data['account_id']
        amount = float(data['amount'])

        if amount % 500 != 0:
            emit('transaction_result', {
                'success': False,
                'message': 'Amount must be multiple of ₱500'
            })
            return

        account = db.get_account(rfid_uid)
        if account['balance'] < amount:
            emit('transaction_result', {
                'success': False,
                'message': 'Insufficient funds'
            })
            return

        new_balance = account['balance'] - amount
        db.update_balance(rfid_uid, new_balance)
        db.log_event(rfid_uid, True, f"Withdraw ₱{amount}")

        emit('transaction_result', {
            'success': True,
            'amount': amount,
            'balance': new_balance
        })

    # Handle print receipt requests from the frontend
    @socketio.on('print_receipt')
    def handle_print_receipt(data):
        try:
            coordinator = get_coordinator(socketio)
            rfid_uid = data.get('rfid_uid')
            title = data.get('title', 'Transaction')
            amount = float(data.get('amount', 0))
            remaining_balance = float(data.get('remaining_balance', 0))
            
            # Use the printer module to print the receipt
            success = coordinator.printer.print_transaction_receipt(
                rfid_uid=rfid_uid,
                title=title,
                amount=amount,
                remaining_balance=remaining_balance
            )
            
            emit('print_result', {'success': success, 'message': 'Receipt printed'}, room=request.sid)
        except Exception as e:
            emit('print_result', {'success': False, 'message': str(e)}, room=request.sid)

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
