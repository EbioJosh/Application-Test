// Sample React component showing integration with Flask backend
import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';

const HardwareApplianceUI = () => {
  const [socket, setSocket] = useState(null);
  const [status, setStatus] = useState('disconnected');
  const [rfidDetected, setRfidDetected] = useState(false);
  const [currentRfid, setCurrentRfid] = useState('');
  const [pinLength, setPinLength] = useState(0);
  const [authResult, setAuthResult] = useState(null);

  useEffect(() => {
    // Connect to Flask-SocketIO server
    const newSocket = io('http://localhost:5000');
    setSocket(newSocket);

    // Listen for connection status
    newSocket.on('connect', () => {
      setStatus('connected');
    });

    newSocket.on('disconnect', () => {
      setStatus('disconnected');
    });

    // Listen for RFID detection
    newSocket.on('rfid_detected', (data) => {
      setRfidDetected(true);
      setCurrentRfid(data.rfid_uid);
      setPinLength(0);
      setAuthResult(null);
    });

    // Listen for PIN request
    newSocket.on('request_pin', (data) => {
      setRfidDetected(true);
      setCurrentRfid(data.rfid_uid);
    });

    // Listen for PIN updates
    newSocket.on('pin_updated', (data) => {
      setPinLength(data.pin_length);
    });

    // Listen for authentication results
    newSocket.on('auth_result', (data) => {
      setAuthResult(data);
      setRfidDetected(false);
    });

    return () => newSocket.close();
  }, []);

  const simulateKeyPress = (key) => {
    if (socket) {
      socket.emit('key_pressed', { key });
    }
  };

  return (
    <div className="appliance-ui">
      <h1>Raspberry Pi Hardware Appliance</h1>
      
      <div className="status">
        <h2>Status: {status}</h2>
      </div>

      {!rfidDetected && !authResult && (
        <div className="waiting">
          <p>Waiting for RFID card...</p>
        </div>
      )}

      {rfidDetected && (
        <div className="pin-entry">
          <h2>RFID Card Detected</h2>
          <p>Card ID: {currentRfid}</p>
          <p>Enter PIN:</p>
          <div className="pin-display">
            {'*'.repeat(pinLength)}
          </div>
          <div className="keypad">
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, '*', 0, '#'].map((key) => (
              <button key={key} onClick={() => simulateKeyPress(key.toString())}>
                {key}
              </button>
            ))}
          </div>
        </div>
      )}

      {authResult && (
        <div className={`auth-result ${authResult.success ? 'success' : 'failure'}`}>
          <h2>Authentication {authResult.success ? 'Successful' : 'Failed'}</h2>
          <p>Card ID: {authResult.rfid_uid}</p>
          <p>Message: {authResult.message}</p>
          <button onClick={() => setAuthResult(null)}>Continue</button>
        </div>
      )}

      <div className="logs">
        <h2>Recent Logs</h2>
        <p>Connect to backend to view logs...</p>
      </div>
    </div>
  );
};

export default HardwareApplianceUI;