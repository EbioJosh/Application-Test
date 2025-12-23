# Raspberry Pi Banking Terminal - Web Application

This is the React frontend for the Raspberry Pi hardware banking terminal system.

## Features

- Card-based authentication using RFID/NFC simulation
- Secure PIN entry via virtual keypad
- Account balance display
- Transaction simulation
- Receipt generation
- Real-time communication with backend via WebSockets

## Integration with Raspberry Pi Backend

The web application communicates with the Flask backend through:

1. **REST API endpoints** for data retrieval and commands
2. **WebSocket connections** for real-time hardware events

### API Endpoints

- `GET /api/status` - System status
- `GET /api/logs` - Authentication logs
- `POST /api/users` - Add new user
- `GET /api/account/:id` - Get account information
- `POST /api/transaction` - Process transaction

### WebSocket Events

- `rfid_detected` - When RFID card is detected
- `request_pin` - When PIN entry is requested
- `key_pressed` - When keypad key is pressed
- `pin_updated` - When PIN buffer changes
- `auth_result` - When authentication completes

## Setup Instructions

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

3. Build for production:
   ```bash
   npm run build
   ```

## Folder Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── App.js
│   ├── App.css
│   ├── index.js
│   └── index.css
├── package.json
└── README.md
```

## Deployment

The built frontend files should be placed in the `static` directory of the Flask backend to be served directly by the Raspberry Pi application.