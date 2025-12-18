"""
API routes for the Raspberry Pi hardware appliance.
"""
import time
from flask import Blueprint, jsonify, request, send_from_directory
from flask_socketio import emit
from app.models.database import db
from app.hardware.coordinator import get_coordinator
import os

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/status', methods=['GET'])
def get_status():
    """Get system status."""
    return jsonify({
        'status': 'online',
        'message': 'System is running'
    })

@api_bp.route('/api/users', methods=['POST'])
def add_user():
    """Add a new user."""
    data = request.get_json()
    
    if not data or 'rfid_uid' not in data or 'pin' not in data:
        return jsonify({'error': 'Missing rfid_uid or pin'}), 400
    
    rfid_uid = data['rfid_uid']
    pin = data['pin']
    
    if len(pin) < 4:
        return jsonify({'error': 'PIN must be at least 4 characters'}), 400
    
    success = db.add_user(rfid_uid, pin)
    
    if success:
        return jsonify({'message': 'User added successfully'}), 201
    else:
        return jsonify({'error': 'RFID UID already exists'}), 409

@api_bp.route('/api/logs', methods=['GET'])
def get_logs():
    """Get authentication logs."""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM logs ORDER BY created_at DESC LIMIT 50')
    logs = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify(logs)

@api_bp.route('/')
def index():
    """Serve the React frontend."""
    # Serve the React app's index.html if it exists
    static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')
    index_path = os.path.join(static_dir, 'index.html')
    
    if os.path.exists(index_path):
        return send_from_directory(static_dir, 'index.html')
    else:
        return jsonify({'message': 'Raspberry Pi Hardware Appliance API'})

@api_bp.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files for the React frontend."""
    static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')
    return send_from_directory(static_dir, filename)

@api_bp.route('/api/test_auth', methods=['POST'])
def test_auth():
    """Test endpoint to simulate RFID detection and PIN entry."""
    from flask import current_app
    # Get the coordinator (this is a simplified approach for testing)
    # In a real implementation, you'd pass the socketio instance properly
    return jsonify({'message': 'Test endpoint - implementation would trigger auth flow'})

@api_bp.route('/api/account/<account_id>')
def get_account(account_id):
    """Get account information."""
    # This is a simulation - in a real system, this would fetch from a database
    accounts = {
        '1234': {
            'name': 'John Doe',
            'accountNumber': '**** **** **** 1234',
            'balance': 1250.75,
            'cardUid': account_id
        }
    }
    
    if account_id in accounts:
        return jsonify(accounts[account_id])
    else:
        return jsonify({'error': 'Account not found'}), 404

@api_bp.route('/api/transaction', methods=['POST'])
def process_transaction():
    """Process a transaction."""
    data = request.get_json()
    
    # This is a simulation - in a real system, this would process the transaction
    # and update the database
    
    if not data or 'account_id' not in data or 'amount' not in data:
        return jsonify({'error': 'Missing account_id or amount'}), 400
    
    # Simulate transaction processing
    transaction_id = 'TXN' + str(int(time.time() * 1000) % 1000000)
    
    return jsonify({
        'transaction_id': transaction_id,
        'status': 'success',
        'message': 'Transaction processed successfully'
    })