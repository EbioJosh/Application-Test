import React, { useState, useEffect, useCallback } from 'react';
import io from 'socket.io-client';
import './App.css'; 

// REPLACE with your Raspberry Pi's actual IP address
const SOCKET_URL = 'http://192.168.107.247:5000'; 
const socket = io(SOCKET_URL);

const ATMApp = () => {
  // State Management
  const [view, setView] = useState('INSERT_CARD'); 
  const [account, setAccount] = useState(null);
  const [pinLength, setPinLength] = useState(0);
  const [amount, setAmount] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [lastTx, setLastTx] = useState(null);

  // Helper: Reset all states to initial splash screen
  const resetSession = useCallback(() => {
    console.log("Resetting Session...");
    setView('INSERT_CARD');
    setAccount(null);
    setAmount('');
    setMessage('');
    setError('');
    setPinLength(0);
    setLastTx(null);
    socket.emit('done'); // Notify backend to reset coordinator state
  }, []);

  // Socket.io Event Listeners
  useEffect(() => {
    socket.on('connect', () => console.log("Connected to Pi Backend"));

    // 1. RFID Card Tapped
    socket.on('request_pin', () => {
      setView('PIN');
      setError('');
    });

    // 2. Physical Keypad PIN Feedback
    socket.on('pin_updated', (data) => {
      setPinLength(data.pin_length);
    });

    // 3. Login Result
    socket.on('auth_result', (data) => {
      if (data.success) {
        setAccount(data.account);
        setView('MENU');
      } else {
        setError(data.message);
        setTimeout(() => resetSession(), 2000);
      }
    });

    // 4. Balance Data received from DB
    socket.on('balance_response', (data) => {
      setAccount(prev => ({ ...prev, balance: data.balance }));
      setView('BALANCE');
    });

    // 5. Physical Keypad Withdrawal Entry
    socket.on('amount_updated', (data) => {
      setAmount(data.amount);
    });

    // 6. Physical Keypad '6' pressed during withdrawal
    socket.on('submit_withdrawal_amount', (data) => {
      handleWithdraw(data.amount);
    });

    // 7. Withdrawal Result
    socket.on('transaction_result', (data) => {
      if (data.success) {
        setLastTx(data);
        setView('WITHDRAW_SUCCESS');
        setError('');
      } else {
        setError(data.message);
      }
    });

    // 8. Auto-timeout (30s inactivity)
    socket.on('session_timeout', () => {
      resetSession();
    });

    return () => {
      socket.off('connect');
      socket.off('request_pin');
      socket.off('pin_updated');
      socket.off('auth_result');
      socket.off('balance_response');
      socket.off('amount_updated');
      socket.off('submit_withdrawal_amount');
      socket.off('transaction_result');
      socket.off('session_timeout');
    };
  }, [resetSession]);

  // --- Logic Handlers ---

  const handleWithdraw = (val) => {
    if (!val || parseFloat(val) <= 0) {
      setError("Please enter an amount");
      return;
    }
    socket.emit('withdraw', { 
      rfid_uid: account.rfid_uid, 
      amount: val 
    });
  };

  const checkBalance = () => {
    socket.emit('balance_request', { rfid_uid: account.rfid_uid });
  };

  const printReceipt = (type) => {
    const data = type === 'BALANCE' 
      ? { rfid_uid: account.rfid_uid, title: 'BALANCE INQUIRY', amount: 0, remaining_balance: account.balance }
      : { rfid_uid: account.rfid_uid, title: 'WITHDRAWAL', amount: lastTx.amount, remaining_balance: lastTx.remaining_balance };
    
    socket.emit('print_receipt', data);
    setMessage('Printing Receipt...');
    setTimeout(() => setMessage(''), 4000);
  };

  const startWithdrawalView = () => {
    setView('WITHDRAW_INPUT');
    setAmount('');
    setError('');
    socket.emit('set_state', { state: 'WITHDRAWING' });
  };

  // --- UI Views ---

  return (
    <div className="atm-container">
      {/* 1. INITIAL SPLASH */}
      {view === 'INSERT_CARD' && (
        <div className="screen-center">
          <div className="brand">PiBank ATM</div>
          <h1>Please Insert Card</h1>
          <div className="card-animation">💳</div>
          <p className="hint">Tap your RFID tag to begin</p>
        </div>
      )}

      {/* 2. PIN ENTRY */}
      {view === 'PIN' && (
        <div className="screen">
          <h2>SECURITY CHECK</h2>
          <p>Please enter your 4-digit PIN</p>
          <div className="pin-container">
            {[...Array(pinLength)].map((_, i) => (
              <div key={i} className="pin-dot">●</div>
            ))}
            {[...Array(Math.max(0, 4 - pinLength))].map((_, i) => (
              <div key={i} className="pin-dot empty">○</div>
            ))}
          </div>
          {error && <p className="error-msg">{error}</p>}
          <p className="footer-hint">Confirm with physical key [6]</p>
        </div>
      )}

      {/* 3. MAIN MENU */}
      {view === 'MENU' && (
        <div className="screen">
          <div className="header">Welcome, {account?.name}</div>
          <div className="menu-options">
            <button className="menu-btn" onClick={checkBalance}>
              <span className="icon">💰</span> Check Balance
            </button>
            <button className="menu-btn" onClick={startWithdrawalView}>
              <span className="icon">💸</span> Withdraw Cash
            </button>
            <button className="menu-btn exit" onClick={resetSession}>
              <span className="icon">🚪</span> Exit
            </button>
          </div>
        </div>
      )}

      {/* 4. BALANCE VIEW */}
      {view === 'BALANCE' && (
        <div className="screen">
          <h2>Account Details</h2>
          <div className="data-box">
            <div className="data-row"><span>Account:</span> <strong>{account?.account_number}</strong></div>
            <div className="data-row"><span>Holder:</span> <strong>{account?.name}</strong></div>
            <hr />
            <div className="balance-display">
              <span className="currency">₱</span>
              {account?.balance.toLocaleString(undefined, { minimumFractionDigits: 2 })}
            </div>
          </div>
          <div className="action-row">
            <button className="btn-print" onClick={() => printReceipt('BALANCE')}>Print Receipt</button>
            <button className="btn-done" onClick={resetSession}>Finish</button>
          </div>
          {message && <div className="toast">{message}</div>}
        </div>
      )}

      {/* 5. WITHDRAWAL INPUT */}
      {view === 'WITHDRAW_INPUT' && (
        <div className="screen">
          <h2>Cash Withdrawal</h2>
          <p>Enter amount in multiples of ₱500</p>
          
          <div className="amount-entry">
            <span className="curr">₱</span>
            <input type="text" value={amount} readOnly placeholder="0" />
          </div>

          <div className="preset-container">
            <button onClick={() => setAmount("500")}>₱500</button>
            <button onClick={() => setAmount("1000")}>₱1,000</button>
            <button onClick={() => setAmount("2000")}>₱2,000</button>
          </div>

          {error && <p className="error-msg">{error}</p>}
          
          <div className="action-row">
            <button className="btn-confirm" onClick={() => handleWithdraw(amount)}>Confirm</button>
            <button className="btn-cancel" onClick={() => setView('MENU')}>Cancel</button>
          </div>
        </div>
      )}

      {/* 6. WITHDRAWAL SUCCESS */}
      {view === 'WITHDRAW_SUCCESS' && (
        <div className="screen">
          <div className="success-icon">✅</div>
          <h2>Transaction Successful</h2>
          <p>Please collect your cash from the dispenser.</p>
          <div className="data-box summary">
            <div className="data-row"><span>Withdrawn:</span> <strong>₱{lastTx?.amount}</strong></div>
            <div className="data-row"><span>Remaining:</span> <strong>₱{lastTx?.remaining_balance.toLocaleString()}</strong></div>
          </div>
          <div className="action-row">
            <button className="btn-print" onClick={() => printReceipt('WITHDRAW')}>Print Receipt</button>
            <button className="btn-done" onClick={resetSession}>Done</button>
          </div>
          {message && <div className="toast">{message}</div>}
        </div>
      )}
    </div>
  );
};

export default ATMApp;
