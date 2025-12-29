"""
Printer module for the Raspberry Pi hardware appliance.
Uses CUPS RAW printing for POS58 thermal printer.

IMPORTANT:
- This module NEVER prints automatically.
- Printing only happens when a print_* method is explicitly called.
"""

import subprocess
from datetime import datetime


class Printer:
    def __init__(self, printer_name="POS58"):
        """
        Initialize printer using an existing CUPS RAW queue.
        """
        self.printer_name = printer_name

    # =========================
    # INTERNAL LOW-LEVEL PRINT
    # =========================
    def _send_to_printer(self, text: str) -> bool:
        """
        Send raw ESC/POS-safe text directly to the CUPS printer queue.
        """
        try:
            process = subprocess.Popen(
                ["lp", "-d", self.printer_name, "-o", "raw"],
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            process.communicate(input=text.encode("ascii", "ignore"))
            return True
        except Exception as e:
            print(f"[PRINTER ERROR] {e}")
            return False

    # =========================
    # ATM AUTH RECEIPT
    # =========================
    def print_receipt(self, rfid_uid: str, success: bool, message: str) -> bool:
        """
        Print authentication receipt.
        """
        now = datetime.now()

        receipt_text = (
            "==============================\n"
            "      MINI ATM AUTH LOG       \n"
            "==============================\n"
            f"CARD ID:   {rfid_uid}\n"
            f"STATUS:    {'AUTHORIZED' if success else 'DENIED'}\n"
            f"MSG:       {message}\n"
            f"DATE:      {now.strftime('%Y-%m-%d')}\n"
            f"TIME:      {now.strftime('%H:%M:%S')}\n"
            "==============================\n"
            "\n\n\n"
        )

        return self._send_to_printer(receipt_text)

    # =========================
    # ATM TRANSACTION RECEIPT
    # =========================
    def print_transaction_receipt(
        self,
        rfid_uid: str,
        title: str,
        amount: float,
        remaining_balance: float
    ) -> bool:
        """
        Print transaction receipt (withdrawal, balance inquiry, etc.)
        """
        now = datetime.now()

        # Masking the RFID UID for security like a real ATM (shows only last 4 chars)
        masked_uid = f"****{rfid_uid[-4:]}" if len(rfid_uid) > 4 else rfid_uid

        receipt_text = (
            "       MINI ATM RECEIPT       \n"
            "------------------------------\n"
            f"DATE:      {now.strftime('%Y-%m-%d')}\n"
            f"TIME:      {now.strftime('%H:%M:%S')}\n"
            f"CARD:      {masked_uid}\n"
            f"TRANS:     {title.upper()}\n"
            "------------------------------\n"
            f"AMOUNT:    PHP {amount:.2f}\n"
            f"BALANCE:   PHP {remaining_balance:.2f}\n"
            "------------------------------\n"
            "   Please keep your receipt.  \n"
            "      Thank you for using     \n"
            "        our Mini ATM!         \n"
            "\n\n\n\n"
        )

        return self._send_to_printer(receipt_text)
