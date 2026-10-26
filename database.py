import sqlite3
from datetime import datetime

DB_NAME = "reminders.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                trigger_time TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Ожидает',
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()

def add_reminder(title, description, trigger_time):
    now_str = datetime.now().strftime("%d.%m.%Y %H:%M")
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reminders (title, description, trigger_time, status, created_at)
            VALUES (?, ?, ?, 'Ожидает', ?)
        """, (title, description, trigger_time, now_str))
        conn.commit()

def get_reminders(status_filter="Все"):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        if status_filter and status_filter != "Все":
            cursor.execute("SELECT id, title, description, trigger_time, status, created_at FROM reminders WHERE status = ? ORDER BY trigger_time ASC", (status_filter,))
        else:
            cursor.execute("SELECT id, title, description, trigger_time, status, created_at FROM reminders ORDER BY trigger_time ASC")
        return cursor.fetchall()

def get_stats():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status, COUNT(*) FROM reminders GROUP BY status")
        rows = cursor.fetchall()
        stats = {"Всего": 0, "Ожидает": 0, "Готово": 0, "Просрочено": 0}
        for status, count in rows:
            if status in stats:
                stats[status] = count
            stats["Всего"] += count
        return stats

def get_due_reminders():
    # Формат времени для проверки совпадает с тем, что генерируют кнопки быстрых минут
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, description FROM reminders WHERE trigger_time <= ? AND status = 'Ожидает'", (now_str,))
        return cursor.fetchall()

def set_status(reminder_id, status):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE reminders SET status = ? WHERE id = ?", (status, reminder_id))
        conn.commit()
