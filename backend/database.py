import sqlite3
import os
from typing import Optional, Dict

DB_FILE = "bookings.db"

def init_db():
    """
    Ensures that the SQLite database and 'bookings' table exist.
    Creates the table if it does not exist.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create the bookings table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            booking_number TEXT PRIMARY KEY,
            full_name TEXT,
            check_in_date TEXT,
            check_out_date TEXT,
            num_guests INTEGER,
            payment_method TEXT,
            breakfast_included TEXT,
            status TEXT,
            language TEXT
        )
    """)
    conn.commit()
    conn.close()

def upsert_booking(context: Dict) -> None:
    """
    Inserts or updates a booking in the 'bookings' table based on booking_number.
    If booking_number doesn't exist in the table, a new row is inserted.
    Otherwise, the existing row is updated.
    """
    booking_number = context.get("booking_number")
    if not booking_number:
        raise ValueError("Cannot upsert booking without a booking_number.")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Upsert logic using INSERT OR REPLACE 
    # (Alternatively, you can do a SELECT to see if it exists and then UPDATE or INSERT)
    cursor.execute("""
        INSERT OR REPLACE INTO bookings (
            booking_number,
            full_name,
            check_in_date,
            check_out_date,
            num_guests,
            payment_method,
            breakfast_included,
            status,
            language
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        booking_number,
        context.get("full_name") or "",
        context.get("check_in_date") or "",
        context.get("check_out_date") or "",
        context.get("num_guests") or 0,
        context.get("payment_method") or "",
        str(context.get("breakfast_included")) if context.get("breakfast_included") is not None else "",
        context.get("status") or "draft",
        context.get("language") or "English"
    ))
    conn.commit()
    conn.close()

def get_booking(booking_number: str) -> Optional[Dict]:
    """
    Retrieves a booking from the database by booking_number.
    Returns a dictionary with the booking details, or None if not found.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings WHERE booking_number = ?", (booking_number,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    # Map the row to a dict matching the context structure
    # row columns: booking_number, full_name, check_in_date, check_out_date, num_guests, payment_method, breakfast_included, status, language
    return {
        "booking_number": row[0],
        "full_name": row[1],
        "check_in_date": row[2],
        "check_out_date": row[3],
        "num_guests": row[4],
        "payment_method": row[5],
        "breakfast_included": row[6],
        "status": row[7],
        "language": row[8]
    }

def remove_booking(booking_number: str) -> None:
    """
    Cancels (deletes) a booking from the database by booking_number.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bookings WHERE booking_number = ?", (booking_number,))
    conn.commit()
    conn.close()
