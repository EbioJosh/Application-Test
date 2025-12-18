# Raspberry Pi Hardware Appliance

A Flask-based embedded system for RFID authentication with thermal printing capabilities and web interface.

## Features
- RFID authentication with PIN validation
- Matrix keypad input handling
- Thermal printer receipt generation
- Real-time status updates via WebSockets
- Local SQLite storage for credentials and logs
- React web application served by Flask
- Account information display
- Transaction simulation
- Receipt generation

## Test Environment

For testing without actual hardware, we provide a simplified version that simulates all hardware components. See [TEST_ENVIRONMENT_README.md](TEST_ENVIRONMENT_README.md) for details.

## Hardware Components

- Raspberry Pi (running Raspberry Pi OS Lite 64-bit)
- USB thermal printer (ESC/POS compatible)
- RFID reader connected via SPI (e.g., MFRC522)
- Matrix keypad connected via GPIO

## Software Stack

- Python 3
- Flask
- Flask-SocketIO for WebSockets
- REST API for configuration
- RPi.GPIO for GPIO access
- spidev + MFRC522 library for RFID
- python-escpos for USB printing
- SQLite for local storage
- React for web frontend
- systemd for auto-start

## Architecture

The system follows a strict architecture where Flask is the only component allowed to access hardware:

1. Flask controls GPIO, SPI, and USB
2. Handles RFID reads, keypad scanning, authentication logic, and printer output
3. React web frontend has no direct hardware access
4. React communicates with Flask via HTTP (REST) and WebSockets
5. Flask and React run on the same Raspberry Pi
6. React is built into static files and served by Flask

## Installation

### For Raspberry Pi Deployment:

1. Create and activate a virtual environment (to avoid "externally managed environment" error):
   ```bash
   python3 -m venv rpi-venv
   source rpi-venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Enable SPI interface on Raspberry Pi:
   ```bash
   sudo raspi-config
   # Interfacing Options -> SPI -> Yes
   ```

4. Connect hardware components according to the pin configuration in `app/config.py`

5. Install systemd service:
   ```bash
   sudo cp rpi-hardware-appliance.service /etc/systemd/system/
   sudo systemctl enable rpi-hardware-appliance
   sudo systemctl start rpi-hardware-appliance
   ```

### For Development (on any platform):

1. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

Note: Raspberry Pi specific libraries (RPi.GPIO, spidev, mfrc522) are only available on Raspberry Pi OS.

### Troubleshooting

If you encounter an "externally managed environment" error:
1. Always use a virtual environment as shown above
2. Alternatively, use `pip install --break-system-packages` (not recommended)

## Web Application

The React web application provides a user interface for:
- Card authentication
- PIN entry
- Account information display
- Transaction processing
- Receipt generation

### Building the Web Application

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Build the application:
   ```bash
   npm run build
   ```

4. Copy build files to Flask static directory:
   ```bash
   # On Unix/Linux/Mac
   cp -r build/* ../app/static/
   
   # On Windows
   xcopy /E /I build\* ..\app\static\
   ```

### Development Mode

To run the web application in development mode:

1. Start the Flask backend:
   ```bash
   python run.py
   ```

2. In another terminal, start the React development server:
   ```bash
   cd frontend
   npm start
   ```

The web application will be available at http://localhost:3000 and will proxy API requests to the Flask backend at http://localhost:5000.

## Usage

1. Activate the virtual environment:
   ```bash
   source rpi-venv/bin/activate
   ```

2. Add users via the REST API:
   ```bash
   curl -X POST http://localhost:5000/api/users \
        -H "Content-Type: application/json" \
        -d '{"rfid_uid": "123456789", "pin": "1234"}'
   ```

3. The system will automatically detect RFID cards and prompt for PIN entry via the keypad

4. Authentication results are printed on the thermal printer

5. View logs via the REST API:
   ```bash
   curl http://localhost:5000/api/logs
   ```

## Frontend Integration

The React frontend communicates with the Flask backend using:

1. REST API endpoints for configuration and data retrieval
2. WebSocket connections for real-time hardware events

Key WebSocket events:
- `rfid_detected`: When an RFID card is read
- `request_pin`: When PIN entry is required
- `pin_updated`: When the PIN buffer changes
- `auth_result`: When authentication completes

The frontend is built into static files and served by Flask from the `/static` directory.

## API Endpoints

- `GET /` - Serve React frontend
- `GET /api/status` - System status
- `POST /api/users` - Add new user
- `GET /api/logs` - Authentication logs
- `GET /api/account/<account_id>` - Get account information
- `POST /api/transaction` - Process transaction
- WebSocket events for real-time updates