# modules/db.py
import os
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.environ["DATABASE_URL"]

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id SERIAL PRIMARY KEY,
                email TEXT NOT NULL,
                med TEXT NOT NULL,
                time TIMESTAMP NOT NULL,
                sent BOOLEAN DEFAULT FALSE
            )
        ''')
        conn.commit()

def insert_reminder(email, med, time_obj):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO reminders (email, med, time)
            VALUES (%s, %s, %s)
        ''', (email, med, time_obj))
        conn.commit()

def get_pending_reminders():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, email, med, time FROM reminders
            WHERE sent = FALSE
        ''')
        return cursor.fetchall()

def mark_reminder_sent(reminder_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE reminders SET sent = TRUE WHERE id = %s
        ''', (reminder_id,))
        conn.commit()
