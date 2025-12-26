import sys
import os
import signal

sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app import create_app
from app.hardware.rfid_reader import RFIDReader
from app.hardware.keypad import Keypad
from app.hardware.coordinator import get_coordinator
from app.models.database import db


def main():
    print("Starting Raspberry Pi Banking Appliance")

    # Create Flask app + SocketIO
    app, socketio = create_app()

    # Initialize database
    db.init_db()
    db.add_user("769714493968", "1234")

    # Create coordinator (ONLY place SocketIO is used)
    coordinator = get_coordinator(socketio)

    # Initialize hardware
    rfid_reader = RFIDReader(coordinator)
    keypad = Keypad(coordinator)

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

    print("System running on port 5000")
    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False
    )


if __name__ == "__main__":
    main()
