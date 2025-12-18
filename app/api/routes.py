"""
API routes for the Raspberry Pi hardware appliance.
"""
from flask import Blueprint, jsonify, request
from flask_socketio import emit
from app.models.database import db
from app.hardware.coordinator import get_coordinator

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
    return jsonify({'message': 'Raspberry Pi Hardware Appliance API'})

@api_bp.route('/api/test_auth', methods=['POST'])
def test_auth():
    """Test endpoint to simulate RFID detection and PIN entry."""
    from flask import current_app
    # Get the coordinator (this is a simplified approach for testing)
    # In a real implementation, you'd pass the socketio instance properly
    return jsonify({'message': 'Test endpoint - implementation would trigger auth flow'})