"""
Main application entry point for the Raspberry Pi ATM appliance
"""
import os
import sys
import signal
from flask import Flask
from flask_socketio import SocketIO, emit

from app.hardware.coordinator import get_coordinator
from app.models.database import db


def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    app.config['SECRET_KEY'] = 'atm-secret'

    socketio = SocketIO(
        app,
        cors_allowed_origins="*",
        async_mode="threading"
    )

    # ==============================
    # SOCKET EVENTS
    # ==============================

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

        if not account:
            emit('balance_response', {'error': 'Account not found'})
            return

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
            amount = int(float(data.get('amount', 0)))
        except ValueError:
            emit('transaction_result', {
                'success': False,
                'message': 'Invalid amount'
            })
            return

        # ==============================
        # VALIDATION RULES
        # ==============================

        if amount <= 0 or amount % 500 != 0:
            emit('transaction_result', {
                'success': False,
                'message': 'Please enter a multiple of ₱500'
            })
            return

        account = db.get_account(rfid_uid)
        if not account:
            emit('transaction_result', {
                'success': False,
                'message': 'Account error'
            })
            return

        if account['balance'] < amount:
            emit('transaction_result', {
                'success': False,
                'message': 'Insufficient funds'
            })
            return

        # ==============================
        # SUCCESS PATH
        # ==============================

        new_balance = account['balance'] - amount

        db.record_transaction(
            rfid_uid,
            "WITHDRAWAL",
            amount,
            new_balance
        )

        # 💸 DISPENSE CASH (₱500 = 1 motor run)
        coord.dispense_cash(amount)

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


# =========================================================
# APPLICATION STARTUP
# =========================================================
if __name__ == '__main__':
    app, socketio = create_app()

    # Import hardware AFTER socketio creation
    from app.hardware.rfid_reader import RFIDReader
    from app.hardware.keypad import Keypad

    coordinator = get_coordinator(socketio)

    rfid_reader = RFIDReader(coordinator)
    keypad = Keypad(coordinator)

    coordinator.set_hardware_components(rfid_reader, keypad)

    rfid_reader.start()
    keypad.start()

    def shutdown(sig, frame):
        print("Shutting down ATM system...")
        rfid_reader.stop()
        keypad.stop()

        if coordinator.motor:
            coordinator.motor.cleanup()

        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    print("Raspberry Pi ATM running on port 5000")

    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False
    )
