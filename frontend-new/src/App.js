import React, { useState, useEffect, useCallback } from 'react';
import io from 'socket.io-client';
import './App.css'; 

// Replace with your actual Pi IP
const SOCKET_URL = 'http://192.168.81.247:5000'; 
const socket = io(SOCKET_URL);

const ATMApp = () => {
  // --- State Management ---
  const [view, setView] = useState('INSERT_CARD'); 
  const [account, setAccount] = useState(null);
  const [pinLength, setPinLength] = useState(0);
  const [amount, setAmount] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [lastTx, setLastTx] = useState(null);
  const [isCardPresent, setIsCardPresent] = useState(false);

  // --- Helpers ---
  const resetSession = useCallback(() => {
    console.log("Resetting Session...");
    setView('INSERT_CARD');
    setAccount(null);
    setAmount('');
    setMessage('');
    setError('');
    setPinLength(0);
    setLastTx(null);
    socket.emit('done'); 
  }, []);

  const initiateExitFlow = () => {
    setView('REMOVE_CARD');
  };

  const maskAccountNumber = (accNum) => {
    if (!accNum) return "";
    const visibleDigits = 4;
    const maskedSection = accNum.slice(0, -visibleDigits).replace(/\d/g, "*");
    const visibleSection = accNum.slice(-visibleDigits);
    return maskedSection + " " + visibleSection;
  };

  // --- Effect: Card Removal Detection ---
  useEffect(() => {
    let checkInterval;
    if (view === 'REMOVE_CARD') {
      // Check card status every 3 seconds as requested
      checkInterval = setInterval(() => {
        if (!isCardPresent) {
          clearInterval(checkInterval);
          setView('COOLDOWN');
          setTimeout(() => {
            resetSession();
          }, 5000); // 5 second wait after removal
        }
      }, 3000);
    }
    return () => clearInterval(checkInterval);
  }, [view, isCardPresent, resetSession]);

  // --- Effect: Socket Listeners ---
  useEffect(() => {
    socket.on('connect', () => console.log("Connected to Pi Backend"));

    socket.on('card_status', (data) => {
      setIsCardPresent(data.present);
    });

    socket.on('request_pin', () => {
      setView('PIN');
      setError('');
    });

    socket.on('pin_updated', (data) => {
      setPinLength(data.pin_length);
    });

    socket.on('auth_result', (data) => {
      if (data.success) {
        setAccount(data.account);
        setView('MENU');
      } else {
        setError(data.message);
        setTimeout(() => resetSession(), 2000);
      }
    });

    socket.on('balance_response', (data) => {
      setAccount(prev => ({ ...prev, balance: data.balance }));
      setView('BALANCE');
    });

    socket.on('amount_updated', (data) => {
      setAmount(data.amount);
    });

    socket.on('submit_withdrawal_amount', (data) => {
      handleWithdraw(data.amount);
    });

    socket.on('transaction_result', (data) => {
      if (data.success) {
        setLastTx(data);
        setView('WITHDRAW_SUCCESS');
        setError('');
      } else {
        setError(data.message); // Restores Multiple of 500 / Insufficient balance errors
      }
    });

    socket.on('session_timeout', () => {
      resetSession();
    });

    return () => {
      socket.off('connect');
      socket.off('card_status');
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

  // --- Handlers ---
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

  // --- Rendering ---
  return (
    <div className="atm-container">
      {/* 1. INSERT CARD */}
      {view === 'INSERT_CARD' && (
        <div className="screen-center">
          <div className="brand">PiBank ATM</div>
          <h3>Please Insert Card</h3>
          <div className="card-animation">💳</div>
        </div>
      )}

      {/* 2. PIN ENTRY */}
      {view === 'PIN' && (
        <div className="screen">
          <h2>SECURITY CHECK</h2>
          <div className="pin-container">
            {[...Array(pinLength)].map((_, i) => <div key={i} className="pin-dot">●</div>)}
            {[...Array(Math.max(0, 4 - pinLength))].map((_, i) => <div key={i} className="pin-dot empty">○</div>)}
          </div>
          {error && <p className="error-msg">{error}</p>}
          <p className="footer-hint">Confirm with physical key [#]</p>
        </div>
      )}

      {/* 3. MAIN MENU */}
      {view === 'MENU' && (
        <div className="screen">
          <div className="header">Welcome, {account?.name}</div>
          <div className="menu-options">
            <button className="menu-btn" onClick={() => socket.emit('balance_request', { rfid_uid: account.rfid_uid })}>💰 Check Balance</button>
            <button className="menu-btn" onClick={startWithdrawalView}>💸 Withdraw Cash</button>
            <button className="menu-btn exit" onClick={initiateExitFlow}>🚪 Exit</button>
          </div>
        </div>
      )}

      {/* 4. BALANCE VIEW */}
      {view === 'BALANCE' && (
        <div className="screen">
          <h3>Balance Inquiry</h3>
          <div className="info-box">
            <p>Name: <strong>{account?.name}</strong></p>
            <p>Account: <strong>{maskAccountNumber(account?.account_number)}</strong></p>
            <p className="balance-amt">₱ {account?.balance.toLocaleString()}</p>
          </div>
          <div className="action-row">
            <button className="btn-print" onClick={() => printReceipt('BALANCE')}>Print Receipt</button>
            <button className="btn-confirm" onClick={() => setView('ANOTHER_TRANSACTION')}>Done</button>
          </div>
          {message && <div className="toast">{message}</div>}
        </div>
      )}

      {/* 5. WITHDRAWAL INPUT (Restored Presets & Error) */}
      {view === 'WITHDRAW_INPUT' && (
        <div className="screen">
          <h2>Cash Withdrawal</h2>
          <div className="amount-entry">
            <span className="curr">₱</span>
            <input type="text" value={amount} placeholder="0" style={{ width: '400px', height: '90px', fontSize: '50px', padding: '10px' }} />
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
          <div className="data-box summary">
            <p>Withdrawn: <strong>₱{lastTx?.amount}</strong></p>
            <p>Remaining: <strong>₱{lastTx?.remaining_balance.toLocaleString()}</strong></p>
          </div>
          <div className="action-row">
            <button className="btn-print" onClick={() => printReceipt('WITHDRAW')}>Print Receipt</button>
            <button className="btn-confirm" onClick={() => setView('ANOTHER_TRANSACTION')}>Continue</button>
          </div>
          {message && <div className="toast">{message}</div>}
        </div>
      )}

      {/* 7. ANOTHER TRANSACTION? */}
      {view === 'ANOTHER_TRANSACTION' && (
        <div className="screen">
          <h3>Perform another transaction?</h3>
          <div className="action-row">
            <button className="btn-confirm" onClick={() => setView('MENU')}>YES</button>
            <button className="btn-cancel" onClick={initiateExitFlow}>NO</button>
          </div>
        </div>
      )}

      {/* 8. REMOVE CARD (With Animations) */}
      {view === 'REMOVE_CARD' && (
        <div className="screen-center">
          <h1 className="warning">Please Remove Your Card</h1>
          <div className="card-animation exit">
            <div className="arrow-up">▲</div>
            <div className="card-icon">💳</div>
          </div>
          {isCardPresent ? (
            <div className="blink">⚠️ CARD STILL DETECTED</div>
          ) : (
            <p className="success-text">Detecting removal...</p>
          )}
        </div>
      )}

      {/* 9. COOLDOWN (Final Wait) */}
      {view === 'COOLDOWN' && (
        <div className="screen-center">
          <h6>Thank you for banking with us!</h6>
          <div className="loader"></div>
          <p>Please wait a moment while we reset...</p>
        </div>
      )}
    </div>
  );
};

export default ATMApp;
