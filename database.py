
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "food_orders.db"


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            items TEXT NOT NULL,
            total REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            created_at TEXT NOT NULL DEFAULT (
                datetime('now', 'localtime')
            ),
            completed_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def create_order(customer_name, phone, items, total):
    conn = get_connection()

    cursor = conn.execute("""
        INSERT INTO orders
        (customer_name, phone, items, total, status)
        VALUES (?, ?, ?, ?, 'Pending')
    """, (customer_name, phone, items, total))

    order_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return order_id


def get_all_orders():
    conn = get_connection()

    orders = conn.execute("""
        SELECT * FROM orders
        ORDER BY id ASC
    """).fetchall()

    conn.close()
    return orders


def get_pending_orders():
    conn = get_connection()

    orders = conn.execute("""
        SELECT * FROM orders
        WHERE status IN ('Pending', 'Preparing')
        ORDER BY id ASC
    """).fetchall()

    conn.close()
    return orders


def get_completed_orders():
    conn = get_connection()

    orders = conn.execute("""
        SELECT * FROM orders
        WHERE status = 'Completed'
        ORDER BY id DESC
    """).fetchall()

    conn.close()
    return orders


def get_order(order_id):
    conn = get_connection()

    order = conn.execute("""
        SELECT * FROM orders
        WHERE id = ?
    """, (order_id,)).fetchone()

    conn.close()
    return order


def update_order_status(order_id, status):
    allowed_statuses = ('Preparing', 'Completed')

    if status not in allowed_statuses:
        return False

    conn = get_connection()

    order = conn.execute(
        "SELECT status FROM orders WHERE id = ?",
        (order_id,)
    ).fetchone()

    if order is None:
        conn.close()
        return False

    current_status = order["status"]

    # FIFO: only the earliest unfinished order can be processed.
    first_order = conn.execute("""
        SELECT id, status FROM orders
        WHERE status IN ('Pending', 'Preparing')
        ORDER BY id ASC
        LIMIT 1
    """).fetchone()

    if first_order is None or first_order["id"] != order_id:
        conn.close()
        return False

    # Valid status transitions
    if status == 'Preparing' and current_status != 'Pending':
        conn.close()
        return False

    if status == 'Completed' and current_status != 'Preparing':
        conn.close()
        return False

    if status == 'Preparing':
        conn.execute("""
            UPDATE orders
            SET status = 'Preparing'
            WHERE id = ?
        """, (order_id,))
    else:
        conn.execute("""
            UPDATE orders
            SET status = 'Completed',
                completed_at = datetime('now', 'localtime')
            WHERE id = ?
        """, (order_id,))

    conn.commit()
    conn.close()
    return True
