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
  const [currentTransaction, setCurrentTransaction] = useState(null);
  const [withdrawAmount, setWithdrawAmount] = useState('');
  const [receiptData, setReceiptData] = useState(null);
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
      console.log('PIN_UPDATED RECEIVED:', data);
      setPinLength(data.pin_length);
      setPinBuffer(data.pin_buffer);
    });

    s.on('auth_result', (data) => {
      if (data.success) {
        setAccountInfo({
          name: 'John Doe',
          accountNumber: '**** **** **** 1234',
          balance: 1250.75,
          cardUid: '1234'
        });
        setCurrentView('actionChoice');
        addMessage('Authentication successful - choose action');
      } else {
        addMessage(`Authentication failed: ${data.message}`);
        resetSession();
      }
    });

    // Listen for balance responses from backend
    s.on('balance_response', (data) => {
      if (data && data.balance !== undefined) {
        const receipt = {
          title: 'Balance Inquiry',
          date: new Date().toLocaleString(),
          amount: 0,
          balance: data.balance
        };
        setReceiptData(receipt);
        setCurrentView('receipt');
        addMessage('Received balance from server');
      } else {
        addMessage('Balance inquiry failed');
      }
    });

    s.on('transaction_result', (data) => {
      if (data && data.success !== undefined) {
        const receipt = {
          title: 'Withdrawal',
          date: new Date().toLocaleString(),
          amount: data.amount || 0,
          balance: data.balance || 0
        };
        setReceiptData(receipt);
        setCurrentView('receipt');
        addMessage(data.message || 'Transaction result received');
      } else {
        addMessage('Transaction failed');
      }
    });

    return () => s.close();
  }, []);
  useEffect(() => {
    if (currentView === 'receipt' && receiptData) {
      // slight delay to ensure DOM updates
      const t = setTimeout(() => {
        printReceipt();
      }, 300);
      return () => clearTimeout(t);
    }
  }, [currentView, receiptData]);

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

  const handleChooseBalance = () => {
    if (!accountInfo || !socket) return;
    // Ask backend for balance; backend will print and respond with 'balance_response'
    socket.emit('balance_request', { account_id: accountInfo.cardUid });
    addMessage('Requested balance from server');
  };

  const submitWithdraw = () => {
    const amt = parseFloat(withdrawAmount || '0');
    if (!accountInfo || !socket || isNaN(amt) || amt <= 0) {
      addMessage('Invalid withdraw amount or no connection');
      return;
    }

    socket.emit('withdraw', { account_id: accountInfo.cardUid, amount: amt });
    addMessage(`Requested withdrawal of $${amt.toFixed(2)}`);
  };

  const printReceipt = () => {
    // Trigger browser print for the receipt element
    // A simple approach: open a new window with receipt HTML for printing
    const receiptEl = document.getElementById('receipt');
    if (!receiptEl) {
      window.print();
      return;
    }
    const newWindow = window.open('', '_blank', 'width=600,height=600');
    if (!newWindow) {
      window.print();
      return;
    }
    newWindow.document.write('<html><head><title>Receipt</title></head><body>');
    newWindow.document.write(receiptEl.innerHTML);
    newWindow.document.write('</body></html>');
    newWindow.document.close();
    newWindow.focus();
    newWindow.print();
    newWindow.close();
    addMessage('Receipt printed');
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

        {currentView === 'actionChoice' && accountInfo && (
          <div className="screen action-screen">
            <h2>Welcome, {accountInfo.name}</h2>
            <p>Choose an action:</p>
            <div style={{ marginTop: '12px' }}>
              <button onClick={() => handleChooseBalance()}>Check Balance</button>
              <button onClick={() => setCurrentView('withdraw')} style={{ marginLeft: '12px' }}>Withdraw</button>
              <button onClick={resetSession} style={{ marginLeft: '12px' }}>Cancel</button>
            </div>
          </div>
        )}

        {currentView === 'withdraw' && accountInfo && (
          <div className="screen withdraw-screen">
            <h2>Withdraw</h2>
            <p>Account: {accountInfo.accountNumber}</p>
            <div style={{ marginTop: '10px' }}>
              <input type="number" placeholder="Amount" value={withdrawAmount} onChange={(e) => setWithdrawAmount(e.target.value)} />
              <button onClick={() => submitWithdraw()} style={{ marginLeft: '8px' }}>Submit</button>
              <button onClick={() => setCurrentView('actionChoice')} style={{ marginLeft: '8px' }}>Back</button>
            </div>
          </div>
        )}

        {currentView === 'receipt' && receiptData && (
          <div className="screen receipt-screen" id="receipt">
            <h2>Receipt</h2>
            <div style={{ textAlign: 'left', display: 'inline-block', border: '1px solid #ccc', padding: '12px' }}>
              <div><strong>{receiptData.title}</strong></div>
              <div>{receiptData.date}</div>
              <div>Account: {accountInfo.accountNumber}</div>
              <div>Amount: ${receiptData.amount.toFixed(2)}</div>
              <div>Balance: ${receiptData.balance.toFixed(2)}</div>
              <div style={{ marginTop: '8px' }}>Thank you for using Secure Banking Terminal.</div>
            </div>

            <div style={{ marginTop: '12px' }}>
              <button onClick={() => printReceipt()}>Print Receipt</button>
              <button onClick={() => { resetSession(); }} style={{ marginLeft: '8px' }}>Done</button>
            </div>
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