"""
Test script for the Raspberry Pi hardware appliance.
"""
import sys
import os
import time
import threading

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_database():
    """Test the database functionality."""
    print("Testing database functionality...")
    
    from app.models.database import db
    
    # Test adding a user
    success = db.add_user("123456789", "1234")
    print(f"Adding user: {'Success' if success else 'Failed (user may already exist)'}")
    
    # Test authenticating the user
    auth_result = db.authenticate_user("123456789", "1234")
    print(f"Authenticating user: {'Success' if auth_result else 'Failed'}")
    
    # Test logging an event
    db.log_event("123456789", True, "Test authentication")
    print("Logged authentication event")
    
    # Test retrieving logs
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as count FROM logs')
    count = cursor.fetchone()['count']
    conn.close()
    print(f"Total log entries: {count}")

def test_hardware_modules():
    """Test the hardware modules."""
    print("\nTesting hardware modules...")
    
    # We can't fully test hardware modules without the actual hardware
    # But we can test that they import correctly
    try:
        from app.hardware.rfid_reader import RFIDReader
        from app.hardware.keypad import Keypad
        from app.hardware.printer import Printer
        from app.hardware.coordinator import AuthCoordinator
        print("All hardware modules imported successfully")
        return True
    except Exception as e:
        print(f"Error importing hardware modules: {e}")
        return False

def test_api_endpoints():
    """Test the API endpoints."""
    print("\nTesting API endpoints...")
    
    # Test creating the Flask app
    try:
        from app import create_app
        app, socketio = create_app()
        print("Flask app created successfully")
        return True
    except Exception as e:
        print(f"Error creating Flask app: {e}")
        return False

def main():
    """Run all tests."""
    print("Raspberry Pi Hardware Appliance - Test Suite")
    print("=" * 50)
    
    test_database()
    test_hardware_modules()
    test_api_endpoints()
    
    print("\n" + "=" * 50)
    print("Test suite completed.")

if __name__ == '__main__':
    main()