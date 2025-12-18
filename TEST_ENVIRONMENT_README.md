# Raspberry Pi 4B Hardware Appliance - Test Environment

This is a simplified version of the full hardware appliance designed specifically for testing on a Raspberry Pi 4B without actual hardware components.

## Features

- Simulated RFID card reading
- Simulated keypad input
- Authentication against SQLite database
- WebSocket event emission
- REST API endpoints
- No actual hardware required

## Setup Instructions

### On Your Development Machine

1. Run the preparation script:
   ```
   prepare-pi4b-test.bat
   ```

2. Transfer the generated `rpi4b-hardware-test.zip` to your Raspberry Pi 4B

### On Your Raspberry Pi 4B

1. Extract the package:
   ```bash
   unzip rpi4b-hardware-test.zip
   cd pi4b-test-package
   ```

2. Make the setup script executable and run it:
   ```bash
   chmod +x setup-pi4b-test.sh
   ./setup-pi4b-test.sh
   ```

3. Run the test application:
   ```bash
   ./run_test.sh
   ```

## Test Credentials

- RFID UID: `123456789`
- PIN: `1234`

## API Endpoints

- `GET /api/status` - System status
- `GET /api/logs` - Authentication logs
- `POST /api/users` - Add new user

## WebSocket Events

- `rfid_detected` - When RFID card is detected
- `request_pin` - When PIN entry is requested
- `key_pressed` - When keypad key is pressed
- `pin_updated` - When PIN buffer changes
- `auth_result` - When authentication completes

## Running as a Service

To run the application as a systemd service:

```bash
sudo cp rpi-hardware-test.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable rpi-hardware-test
sudo systemctl start rpi-hardware-test
```