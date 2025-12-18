# Raspberry Pi Banking Terminal - Web Application Guide

## Overview

The web application for the Raspberry Pi Banking Terminal provides a user-friendly interface for interacting with the hardware system. It handles card authentication, PIN verification, account information display, transaction processing, and receipt generation.

## Features

1. **User Authentication**
   - Card-based login using RFID/NFC simulation
   - Secure PIN entry via virtual keypad
   - Real-time authentication feedback

2. **Account Management**
   - Account information display
   - Balance visualization
   - Transaction history

3. **Transaction Processing**
   - Cash withdrawal simulation
   - Amount validation
   - Balance updates

4. **Receipt Generation**
   - Transaction receipt display
   - Print simulation
   - Transaction details

## Architecture

The web application follows a client-server architecture:

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

## Communication Protocol

### REST API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serve React frontend |
| `/api/status` | GET | System status |
| `/api/users` | POST | Add new user |
| `/api/logs` | GET | Authentication logs |
| `/api/account/<account_id>` | GET | Get account information |
| `/api/transaction` | POST | Process transaction |

### WebSocket Events

| Event | Direction | Description |
|-------|-----------|-------------|
| `rfid_detected` | Server → Client | RFID card detected |
| `request_pin` | Server → Client | Request PIN entry |
| `key_pressed` | Client → Server | Keypad key pressed |
| `pin_updated` | Server → Client | PIN buffer updated |
| `auth_result` | Server → Client | Authentication result |

## Components

### 1. Welcome Screen
- Prompts user to insert/tap card
- Displays current card status
- Provides session reset option

### 2. PIN Entry Screen
- Virtual keypad for PIN input
- Visual feedback for entered digits
- Submit and clear functionality

### 3. Account Screen
- User account information
- Current balance display
- Transaction initiation

### 4. Receipt Screen
- Transaction details
- Print simulation
- Session completion options

## Integration with Backend

The React frontend communicates with the Flask backend through:

1. **HTTP Requests**: For data operations (GET/POST)
2. **WebSocket Connections**: For real-time hardware events
3. **Static File Serving**: Backend serves built frontend files

## Development Workflow

### Prerequisites
- Node.js (v14 or higher)
- npm (v6 or higher)

### Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

### Development Mode
1. Start the Flask backend:
   ```bash
   # In the project root directory
   python run.py
   ```

2. Start the React development server:
   ```bash
   # In the frontend directory
   npm start
   ```

3. Access the application at http://localhost:3000

### Production Build
1. Build the React application:
   ```bash
   npm run build
   ```

2. Copy build files to Flask static directory:
   ```bash
   # On Unix/Linux/Mac
   cp -r build/* ../app/static/
   
   # On Windows
   xcopy /E /I build\* ..\app\static\
   ```

3. Access the application at http://localhost:5000

## Customization

### Styling
- Modify `App.css` for visual changes
- Use CSS variables for consistent theming

### Functionality
- Extend `App.js` for additional features
- Add new API endpoints in `routes.py`
- Implement new WebSocket events as needed

## Troubleshooting

### Common Issues

1. **WebSocket Connection Failed**
   - Ensure Flask backend is running
   - Check if the correct port is used (5000)
   - Verify network connectivity

2. **API Requests Failing**
   - Confirm backend endpoints are implemented
   - Check request/response formats
   - Validate authentication if required

3. **Static Files Not Loading**
   - Ensure build files are copied to `app/static/`
   - Restart Flask server after copying files
   - Check file permissions

### Debugging Tips

1. Use browser developer tools to inspect:
   - Network requests
   - Console logs
   - Component state

2. Add console.log statements in React components:
   ```javascript
   console.log('Debug information:', variable);
   ```

3. Check Flask backend logs for errors:
   ```bash
   # In the terminal where Flask is running
   ```

## Security Considerations

1. **PIN Security**
   - PINs are masked in the UI
   - Transmitted securely over WebSocket
   - Validated on the backend

2. **Data Protection**
   - Account information is simulated in this example
   - In production, use HTTPS for all communications
   - Implement proper authentication for API endpoints

3. **Input Validation**
   - All user inputs are validated
   - Prevent XSS attacks through proper escaping
   - Sanitize data before database storage

## Performance Optimization

1. **Bundle Size**
   - Use code splitting for large applications
   - Remove unused dependencies
   - Optimize images and assets

2. **Rendering**
   - Implement React.memo for performance
   - Use useMemo/useCallback for expensive calculations
   - Virtualize long lists

3. **Network**
   - Minimize WebSocket events
   - Cache frequently accessed data
   - Implement request debouncing where appropriate

## Future Enhancements

1. **Additional Features**
   - Deposit simulation
   - Transfer functionality
   - Account settings

2. **UI Improvements**
   - Animations and transitions
   - Dark mode support
   - Responsive design enhancements

3. **Technical Improvements**
   - State management with Redux/Zustand
   - TypeScript migration
   - Unit testing implementation