# Raspberry Pi Hardware Appliance - Technical Documentation

## System Overview

This document describes a Raspberry Pi-based hardware system that implements an RFID authentication system with thermal printing capabilities. The system follows a strict architectural pattern where Flask is the only component allowed to access hardware.

## Architecture

### High-Level Architecture

```
┌─────────────────────┐    HTTP/WebSocket    ┌──────────────────┐
│   React Frontend    │ ◄──────────────────► │   Flask Backend  │
└─────────────────────┘                      └─────────┬────────┘
                                                       │
                                              Hardware Access
                                                       │
┌─────────────────────┐                      ┌─────────▼────────┐
│  RFID Reader (SPI)  │ ◄──────────────────► │                  │
└─────────────────────┘         GPIO        │  Hardware Layer  │
┌─────────────────────┐                      │                  │
│  Keypad (GPIO)     │ ◄──────────────────► │                  │
└─────────────────────┘                      └─────────┬────────┘
┌─────────────────────┐                                │ USB
│ Thermal Printer     │ ◄──────────────────────────────┘
└─────────────────────┘
```

### Component Responsibilities

1. **Flask Backend**:
   - Controls all hardware access (GPIO, SPI, USB)
   - Handles RFID reads, keypad scanning, authentication logic
   - Manages printer output
   - Provides REST API for configuration/admin actions
   - Emits real-time events via WebSockets

2. **React Frontend**:
   - Browser-based UI only
   - No direct hardware access
   - Communicates with Flask via HTTP/WebSockets
   - Built into static files and served by Flask

3. **Hardware Layer**:
   - Runs in background threads
   - Uses thread-safe communication (queues/events)
   - Continues working even if UI is closed

## Implementation Details

### Hardware Modules

#### RFID Reader (`app/hardware/rfid_reader.py`)

- Uses MFRC522 library for RFID communication via SPI
- Runs in a background thread continuously polling for cards
- Emits `rfid_detected` WebSocket event when card is read
- Requests PIN entry via `request_pin` WebSocket event

#### Keypad (`app/hardware/keypad.py`)

- Interfaces with matrix keypad via GPIO pins
- Scans for key presses in a background thread
- Emits `key_pressed` WebSocket event for each key press
- Supports digit keys, enter (#), and clear (*) keys

#### Printer (`app/hardware/printer.py`)

- Uses python-escpos library for ESC/POS compatible printers
- Prints authentication receipts with timestamp
- Shows success/failure status and messages

#### Coordinator (`app/hardware/coordinator.py`)

- Manages authentication flow between components
- Handles RFID detection and PIN entry coordination
- Processes authentication logic
- Logs events to database
- Controls printer output

### Data Layer

#### Database (`app/models/database.py`)

- Uses SQLite for local storage
- Stores RFID UIDs and hashed PINs in `users` table
- Logs authentication events in `logs` table
- Implements secure PIN hashing with SHA-256

### API Layer

#### Routes (`app/api/routes.py`)

- `/api/status` - System health check
- `/api/users` - User management (POST to add users)
- `/api/logs` - Retrieve authentication logs
- `/` - Serve React frontend

### Configuration

#### Config (`app/config.py`)

- Centralized configuration management
- Environment variable overrides
- Hardware-specific settings (GPIO pins, etc.)

## Threading Model

The system uses a multi-threaded approach for hardware access:

1. **Main Thread**: Runs Flask application and handles HTTP/WebSocket requests
2. **RFID Thread**: Continuously polls RFID reader in background
3. **Keypad Thread**: Continuously scans keypad for key presses
4. **Event Loop**: Flask-SocketIO handles real-time communication

Communication between threads and the main Flask application is done through:
- WebSocket events for real-time updates
- Thread-safe operations for database access
- Queues for passing data between threads (where needed)

## Security Considerations

1. **PIN Storage**: PINs are hashed using SHA-256 before storage
2. **Communication**: WebSocket connections use secure protocols
3. **Access Control**: REST API can be extended with authentication
4. **Physical Security**: Hardware components should be physically secured

## Deployment

### systemd Service

The system includes a systemd service file for automatic startup and crash recovery:

```
[Unit]
Description=Raspberry Pi Hardware Appliance
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/rpi-hardware-appliance
ExecStart=/home/pi/rpi-hardware-appliance/rpi-venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Installation Steps

1. Install Raspberry Pi OS Lite (64-bit)
2. Enable SPI interface via `raspi-config`
3. Create virtual environment to avoid "externally managed environment" error
4. Install Python dependencies in virtual environment
5. Connect hardware components
6. Install and enable systemd service
7. Add users via REST API

### Handling Externally Managed Environment Errors

Modern Linux distributions (including recent Raspberry Pi OS) use the "externally managed environment" protection to prevent accidental system package corruption. To avoid this issue:

1. Always use virtual environments for Python projects
2. The provided setup scripts automatically create and use virtual environments
3. If manually installing, create a virtual environment first:
   ```bash
   python3 -m venv rpi-venv
   source rpi-venv/bin/activate
   pip install -r requirements.txt
   ```
4. For systemd service, ensure the ExecStart path points to the virtual environment Python

## Testing

The system includes comprehensive tests:
- Database functionality
- Hardware module imports
- API endpoint creation
- Authentication flow simulation

Tests can be run with the virtual environment activated:
```bash
source rpi-venv/bin/activate
python test_system.py
```

## Extensibility

The modular design allows for easy extensions:
- Additional authentication factors
- More sophisticated logging
- Integration with external systems
- Enhanced UI features