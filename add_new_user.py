import sys
import os
from app.models.database import db

def register_new_user():
    print("--- PiBank User Registration Tool ---")
    
    # 1. Collect User Input
    rfid_uid = input("Scan/Enter RFID UID: ").strip()
    if not rfid_uid:
        print("Error: RFID UID is required.")
        return

    name = input("Enter Full Name: ").strip()
    acc_num = input("Enter Account Number (e.g., **** 1234): ").strip()
    
    try:
        pin = input("Set 4-Digit PIN: ").strip()
        if len(pin) != 4 or not pin.isdigit():
            print("Error: PIN must be exactly 4 digits.")
            return
            
        initial_balance = float(input("Enter Initial Balance: "))
    except ValueError:
        print("Error: Invalid input for PIN or Balance.")
        return

    # 2. Save to Database
    try:
        # Check if user already exists
        if db.get_account(rfid_uid):
            print(f"Error: A user with RFID {rfid_uid} already exists.")
            return

        # Add to 'users' table (Auth)
        db.add_user(rfid_uid, pin)
        
        # Add to 'accounts' table (Details)
        db.create_account(rfid_uid, name, acc_num, initial_balance)
        
        print(f"\n✅ Success! {name} has been registered.")
        print(f"RFID: {rfid_uid} | Balance: ₱{initial_balance:,.2f}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    register_new_user()
