import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import './App.css';

function App() {
  const [socket, setSocket] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [currentView, setCurrentView] = useState('welcome');
  const [rfidUid, setRfidUid] = useState('');
  const [pinLength, setPinLength] = useState(0);
  const [pinBuffer, setPinBuffer] = useState(''); // Added to store actual keys from backend
  const [accountInfo, setAccountInfo] = useState(null);
  const [messages, setMessages] = useState([]);


  useEffect(() => {
    const s = io('http://localhost:5000');
    setSocket(s);

    s.on('connect', () => {
      setConnectionStatus('connected');
      addMessage('Connected to banking system');
    });

    s.on('disconnect', () => {
      setConnectionStatus('disconnected');
      addMessage('Disconnected');
    });

    s.on('rfid_detected', (data) => {
      setRfidUid(data.rfid_uid);
      addMessage(`RFID detected: ${data.rfid_uid}`);
    });

    s.on('request_pin', (data) => {
      setRfidUid(data.rfid_uid);
      setPinLength(0);
      setPinBuffer('');
      setCurrentView('pinEntry');
      addMessage('Enter PIN on physical keypad');
    });


    s.on('pin_updated', (data) => {
      console.log("PIN_UPDATED RECEIVED:", data); // Should appear in browser console
      setPinLength(data.pin_length);
      setPinBuffer(data.pin_buffer);
    });


    s.on('auth_result', (data) => {
      if (data.success) {
        setAccountInfo({
          name: 'John Doe',
          accountNumber: '**** **** **** 1234',
          balance: 1250.75
        });
        setCurrentView('account');
        addMessage('Authentication successful');
      } else {
        addMessage(`Authentication failed: ${data.message}`);
        resetSession();
      }
    });

    return () => s.close();
  }, []);

  const addMessage = (msg) => {
    setMessages(prev => [...prev, `${new Date().toLocaleTimeString()} - ${msg}`]);
  };

  const resetSession = () => {
    setRfidUid('');
    setPinLength(0);
    setPinBuffer('');
    setAccountInfo(null);
    setCurrentView('welcome');
    addMessage('Session reset');
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Secure Banking Terminal</h1>
        <p>Status: {connectionStatus}</p>
      </header>

      <main>
        {currentView === 'welcome' && (
          <div>
            <h2>Insert / Tap Card</h2>
            <p>Current card: {rfidUid || 'None'}</p>
          </div>
        )}

        {currentView === 'pinEntry' && (
          <div className="screen pin-screen">
            <h2>Enter PIN</h2>
            <p>Card: {rfidUid.substring(0, 4)} **** **** ****</p>

            {/* PIN Display: Dots */}
            <div className="pin-display">
              <div className="pin-dots" style={{ fontSize: '2rem', letterSpacing: '10px' }}>
                {'•'.repeat(pinLength)}
              </div>
            </div>

            {/* Actual keys pressed (for testing/debug) */}
            <div className="pin-keys-display" style={{ marginTop: '20px', color: '#888' }}>
              {pinBuffer || 'No keys pressed yet'}
            </div>

            <p style={{ fontSize: '0.9rem', marginTop: '10px', color: '#555' }}>
              Use physical keypad
            </p>
          </div>
        )}

        {currentView === 'account' && accountInfo && (
          <div>
            <h2>Account</h2>
            <p>{accountInfo.name}</p>
            <p>{accountInfo.accountNumber}</p>
            <p>Balance: ${accountInfo.balance.toFixed(2)}</p>
            <button onClick={resetSession}>Logout</button>
          </div>
        )}
      </main>

      <footer style={{ marginTop: '40px', borderTop: '1px solid #ccc', paddingTop: '10px' }}>
        <h4>System Messages</h4>
        <div style={{ height: '150px', overflowY: 'auto', textAlign: 'left', padding: '0 20px' }}>
          {messages.map((m, i) => (
            <div key={i} style={{ fontSize: '0.8rem' }}>{m}</div>
          ))}
        </div>
      </footer>
    </div>
  );
}

export default App;