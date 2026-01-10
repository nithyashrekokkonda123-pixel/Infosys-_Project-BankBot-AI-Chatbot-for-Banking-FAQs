# database/bank_crud.py

import sqlite3
from database.db import get_conn
from database.security import hash_password, verify_password
from datetime import datetime

def create_account(name, acc_no, acc_type, balance, password):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("INSERT OR IGNORE INTO users(name) VALUES (?)", (name,))
    pwd_hash = hash_password(password)

    cur.execute("""
    INSERT INTO accounts(account_number, user_name, account_type, balance, password_hash)
    VALUES (?, ?, ?, ?, ?)
    """, (acc_no, name, acc_type, balance, pwd_hash))

    conn.commit()
    conn.close()

def get_account(acc_no):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    SELECT account_number, user_name, account_type, balance, password_hash
    FROM accounts WHERE account_number=?
    """, (acc_no,))
    row = cur.fetchone()
    conn.close()
    return row

def list_accounts():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT account_number, user_name FROM accounts")
    rows = cur.fetchall()
    conn.close()
    return rows

def transfer_money(from_acc, to_acc, amount, password):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT balance, password_hash FROM accounts WHERE account_number=?",
        (from_acc,)
    )
    row = cur.fetchone()

    if not row:
        conn.close()
        return "❌ Invalid sender account"

    balance, pwd_hash = row

    if not verify_password(password, pwd_hash):
        conn.close()
        return "❌ Incorrect password"

    if balance < amount:
        conn.close()
        return "❌ Insufficient balance"

    # Perform transaction
    cur.execute(
        "UPDATE accounts SET balance = balance - ? WHERE account_number=?",
        (amount, from_acc)
    )
    cur.execute(
        "UPDATE accounts SET balance = balance + ? WHERE account_number=?",
        (amount, to_acc)
    )

    cur.execute("""
        INSERT INTO transactions(from_account, to_account, amount, timestamp)
        VALUES (?, ?, ?, ?)
    """, (from_acc, to_acc, amount, datetime.now().isoformat()))

    conn.commit()
    conn.close()
    return "✅ Transfer Successful"

    
def update_password(acc_no, new_password):
    conn = get_conn()
    cur = conn.cursor()

    new_hash = hash_password(new_password)

    cur.execute("""
    UPDATE accounts
    SET password_hash = ?
    WHERE account_number = ?
    """, (new_hash, acc_no))

    conn.commit()
    conn.close()
    
def save_chat(username, query, intent, confidence):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO chat_history (username, query, intent, confidence, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (username, query, intent, confidence, datetime.now().isoformat()))

    conn.commit()
    conn.close()


def fetch_chat_history():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, username, query, intent, confidence, timestamp
        FROM chat_history
        ORDER BY id DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

# ========== KNOWLEDGE BASE CRUD FUNCTIONS ==========

def add_faq(question, answer, category):
    """Add new FAQ to knowledge base"""
    conn = sqlite3.connect("bankbot.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO knowledge_base (question, answer, category) VALUES (?, ?, ?)",
        (question, answer, category)
    )
    conn.commit()
    conn.close()


def get_all_faqs():
    """Get all FAQs from knowledge base"""
    conn = sqlite3.connect("bankbot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM knowledge_base ORDER BY created_at DESC")
    faqs = cursor.fetchall()
    conn.close()
    return faqs


def search_faqs(search_term):
    """Search FAQs by question or category"""
    conn = sqlite3.connect("bankbot.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM knowledge_base WHERE question LIKE ? OR category LIKE ? ORDER BY created_at DESC",
        (f"%{search_term}%", f"%{search_term}%")
    )
    faqs = cursor.fetchall()
    conn.close()
    return faqs


def get_faqs_by_category(category):
    """Get FAQs by specific category"""
    conn = sqlite3.connect("bankbot.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM knowledge_base WHERE category = ? ORDER BY created_at DESC",
        (category,)
    )
    faqs = cursor.fetchall()
    conn.close()
    return faqs


def update_faq(faq_id, question, answer, category):
    """Update existing FAQ"""
    conn = sqlite3.connect("bankbot.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE knowledge_base SET question=?, answer=?, category=? WHERE id=?",
        (question, answer, category, faq_id)
    )
    conn.commit()
    conn.close()


def delete_faq(faq_id):
    """Delete FAQ from knowledge base"""
    conn = sqlite3.connect("bankbot.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM knowledge_base WHERE id=?", (faq_id,))
    conn.commit()
    conn.close()