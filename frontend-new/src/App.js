import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import './App.css';

function App() {
  const [socket, setSocket] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [currentView, setCurrentView] = useState('welcome');
  const [rfidUid, setRfidUid] = useState('');
  const [pinLength, setPinLength] = useState(0);
  const [pinBuffer, setPinBuffer] = useState('');
  const [accountInfo, setAccountInfo] = useState(null);
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
          name: data.account.name,
          accountNumber: data.account.account_number,
          balance: data.account.balance,
          cardUid: data.account.rfid_uid
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

    // Listen for print result from backend
    s.on('print_result', (data) => {
      if (data.success) {
        addMessage('Receipt printed successfully');
      } else {
        addMessage(`Print failed: ${data.message}`);
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
    setReceiptData(null);
    setCurrentView('welcome');
    addMessage('Session reset');
  };

  const handleChooseBalance = () => {
    if (!accountInfo || !socket) return;
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
    setWithdrawAmount(''); 
  };

  const printReceipt = () => {
    if (!socket || !receiptData || !rfidUid) {
      addMessage('Cannot print: No connection or receipt data');
      return;
    }

    socket.emit('print_receipt', {
      rfid_uid: rfidUid,
      title: receiptData.title,
      amount: receiptData.amount,
      remaining_balance: receiptData.balance
    });
    
    addMessage('Sending receipt to printer...');
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

            <div className="pin-display">
              <div className="pin-dots" style={{ fontSize: '2rem', letterSpacing: '10px' }}>
                {'•'.repeat(pinLength)}
              </div>
            </div>

            <div className="pin-keys-display" style={{ marginTop: '20px', color: '#888' }}>
              {pinBuffer || 'No keys pressed yet'}
            </div>

            <p style={{ fontSize: '0.9rem', marginTop: '10px', color: '#555' }}>
              Use physical keypad
            </p>
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
            <p>Available Balance: ${accountInfo.balance?.toFixed(2)}</p>
            <div style={{ marginTop: '10px' }}>
              <input 
                type="number" 
                placeholder="Amount" 
                value={withdrawAmount} 
                onChange={(e) => setWithdrawAmount(e.target.value)}
                min="0"
                step="0.01"
              />
              <button onClick={() => submitWithdraw()} style={{ marginLeft: '8px' }}>Submit</button>
              <button onClick={() => setCurrentView('actionChoice')} style={{ marginLeft: '8px' }}>Back</button>
            </div>
          </div>
        )}

        {currentView === 'receipt' && receiptData && (
          <div className="screen receipt-screen">
            <h2>Receipt</h2>
            <div style={{ textAlign: 'left', display: 'inline-block', border: '1px solid #ccc', padding: '12px' }}>
              <div><strong>{receiptData.title}</strong></div>
              <div>{receiptData.date}</div>
              <div>Account: {accountInfo?.accountNumber || 'N/A'}</div>
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
