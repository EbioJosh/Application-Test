import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import axios from 'axios';
import './App.css';

function App() {
  const [socket, setSocket] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [currentView, setCurrentView] = useState('welcome'); // welcome, pinEntry, account, transaction, receipt
  const [rfidUid, setRfidUid] = useState('');
  const [pin, setPin] = useState('');
  const [accountInfo, setAccountInfo] = useState(null);
  const [transactionAmount, setTransactionAmount] = useState('');
  const [receiptData, setReceiptData] = useState(null);
  const [messages, setMessages] = useState([]);

  // Initialize SocketIO connection
  useEffect(() => {
    const newSocket = io('http://localhost:5000');
    setSocket(newSocket);

    newSocket.on('connect', () => {
      setConnectionStatus('connected');
      addMessage('Connected to banking system');
    });

    newSocket.on('disconnect', () => {
      setConnectionStatus('disconnected');
      addMessage('Disconnected from banking system');
    });

    // Listen for RFID detection
    newSocket.on('rfid_detected', (data) => {
      setRfidUid(data.rfid_uid);
      addMessage(`Card detected: ${data.rfid_uid}`);
    });

    // Listen for PIN request
    newSocket.on('request_pin', (data) => {
      setRfidUid(data.rfid_uid);
      setCurrentView('pinEntry');
      setPin('');
      addMessage('Please enter your PIN');
    });

    // Listen for PIN updates
    newSocket.on('pin_updated', (data) => {
      // This would update a visual indicator of PIN length
    });

    // Listen for authentication results
    newSocket.on('auth_result', (data) => {
      if (data.success) {
        // Simulate fetching account info
        setAccountInfo({
          name: 'John Doe',
          accountNumber: '**** **** **** 1234',
          balance: 1250.75,
          cardUid: data.rfid_uid
        });
        setCurrentView('account');
        addMessage('Authentication successful');
      } else {
        addMessage('Authentication failed: ' + data.message);
        setCurrentView('welcome');
      }
    });

    return () => newSocket.close();
  }, []);

  const addMessage = (message) => {
    setMessages(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`]);
  };

  const handlePinSubmit = () => {
    if (socket && rfidUid && pin) {
      // Simulate sending each digit and then the enter key
      for (let i = 0; i < pin.length; i++) {
        socket.emit('key_pressed', { key: pin[i] });
      }
      socket.emit('key_pressed', { key: '#' }); // Enter key
      addMessage('PIN submitted for verification');
    }
  };

  const handleTransaction = () => {
    if (transactionAmount && !isNaN(transactionAmount)) {
      // Simulate transaction
      const newBalance = accountInfo.balance - parseFloat(transactionAmount);
      setAccountInfo(prev => ({
        ...prev,
        balance: newBalance
      }));
      
      // Generate receipt data
      setReceiptData({
        date: new Date().toLocaleString(),
        account: accountInfo.accountNumber,
        amount: parseFloat(transactionAmount),
        balance: newBalance,
        transactionId: 'TXN' + Math.floor(Math.random() * 1000000)
      });
      
      setCurrentView('receipt');
      addMessage(`Transaction processed: $${transactionAmount}`);
    }
  };

  const resetSession = () => {
    setRfidUid('');
    setPin('');
    setAccountInfo(null);
    setTransactionAmount('');
    setReceiptData(null);
    setCurrentView('welcome');
    addMessage('Session reset');
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Secure Banking Terminal</h1>
        <div className="status-indicator">
          <span className={`status-dot ${connectionStatus}`}></span>
          <span>System: {connectionStatus}</span>
        </div>
      </header>

      <main className="App-main">
        {/* Welcome Screen */}
        {currentView === 'welcome' && (
          <div className="screen welcome-screen">
            <h2>Welcome to Secure Banking</h2>
            <div className="card-animation">
              <div className="card-reader">
                <p>Please insert or tap your card</p>
                <div className="card-slot"></div>
              </div>
            </div>
            <div className="instructions">
              <p>Current card in system: {rfidUid || 'None'}</p>
              <button onClick={resetSession}>Reset Session</button>
            </div>
          </div>
        )}

        {/* PIN Entry Screen */}
        {currentView === 'pinEntry' && (
          <div className="screen pin-screen">
            <h2>Enter PIN</h2>
            <p>Card: {rfidUid.substring(0, 4)} **** **** ****</p>
            
            <div className="pin-display">
              <div className="pin-dots">
                {'•'.repeat(pin.length)}
              </div>
            </div>
            
            <div className="keypad">
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, '*', 0, '#'].map((key) => (
                <button 
                  key={key} 
                  onClick={() => {
                    if (key === '#' || key === '*') {
                      // Special keys
                      if (key === '#') handlePinSubmit();
                    } else {
                      // Number keys
                      setPin(prev => prev + key);
                    }
                  }}
                  className="keypad-button"
                >
                  {key}
                </button>
              ))}
            </div>
            
            <div className="pin-actions">
              <button onClick={() => setPin(prev => prev.slice(0, -1))}>Clear</button>
              <button onClick={handlePinSubmit} disabled={pin.length < 4}>Submit</button>
            </div>
          </div>
        )}

        {/* Account Screen */}
        {currentView === 'account' && accountInfo && (
          <div className="screen account-screen">
            <h2>Account Information</h2>
            
            <div className="account-details">
              <div className="account-holder">
                <h3>{accountInfo.name}</h3>
                <p>Account: {accountInfo.accountNumber}</p>
              </div>
              
              <div className="balance-section">
                <h3>Available Balance</h3>
                <p className="balance">${accountInfo.balance.toFixed(2)}</p>
              </div>
            </div>
            
            <div className="transaction-section">
              <h3>Withdraw Funds</h3>
              <div className="amount-input">
                <label>Amount ($):</label>
                <input 
                  type="number" 
                  value={transactionAmount}
                  onChange={(e) => setTransactionAmount(e.target.value)}
                  placeholder="0.00"
                  min="0"
                  step="0.01"
                />
                <button onClick={handleTransaction} disabled={!transactionAmount || isNaN(transactionAmount)}>
                  Withdraw
                </button>
              </div>
            </div>
            
            <div className="account-actions">
              <button onClick={resetSession}>Logout</button>
            </div>
          </div>
        )}

        {/* Receipt Screen */}
        {currentView === 'receipt' && receiptData && (
          <div className="screen receipt-screen">
            <h2>Transaction Receipt</h2>
            
            <div className="receipt-content">
              <div className="receipt-header">
                <h3>Banking Terminal</h3>
                <p>{receiptData.date}</p>
              </div>
              
              <div className="receipt-details">
                <p><strong>Account:</strong> {receiptData.account}</p>
                <p><strong>Transaction ID:</strong> {receiptData.transactionId}</p>
                <p><strong>Amount:</strong> ${receiptData.amount.toFixed(2)}</p>
                <p><strong>New Balance:</strong> ${receiptData.balance.toFixed(2)}</p>
              </div>
              
              <div className="receipt-footer">
                <p>Thank you for using our services</p>
                <div className="barcode-placeholder"></div>
              </div>
            </div>
            
            <div className="receipt-actions">
              <button onClick={() => {
                // Simulate printing
                addMessage('Receipt printed');
                resetSession();
              }}>
                Print Receipt & Finish
              </button>
              <button onClick={resetSession}>Finish Without Printing</button>
            </div>
          </div>
        )}
      </main>

      <footer className="App-footer">
        <div className="messages-panel">
          <h4>System Messages</h4>
          <div className="messages-list">
            {messages.map((msg, index) => (
              <div key={index} className="message-item">{msg}</div>
            ))}
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;