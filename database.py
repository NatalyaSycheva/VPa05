import sqlite3
from datetime import datetime

DB_NAME = "reminders.db"

def init_db():
    """Создает таблицу, если она еще не создана."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                trigger_time TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Ожидает'
            )
        """)
        conn.commit()

def check_overdue():
    """Автоматически переводит просроченные напоминания в статус 'Просрочено'."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE reminders 
            SET status = 'Просрочено' 
            WHERE trigger_time < ? AND status = 'Ожидает'
        """, (now_str,))
        conn.commit()

def add_reminder(title, description, trigger_time):
    """Добавляет новое напоминание."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reminders (title, description, trigger_time, status)
            VALUES (?, ?, ?, 'Ожидает')
        """, (title, description, trigger_time))
        conn.commit()

def delete_reminder(reminder_id):
    """Удаляет напоминание по ID."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
        conn.commit()

def update_status(reminder_id, new_status):
    """Обновляет статус ('Готово', 'Отменено' и т.д.)."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE reminders SET status = ? WHERE id = ?", (new_status, reminder_id))
        conn.commit()

def get_reminders(status_filter=None):
    """Возвращает список напоминаний с возможностью фильтрации."""
    check_overdue()  # Обновляем статусы перед выгрузкой
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        if status_filter and status_filter != "Все":
            cursor.execute("SELECT * FROM reminders WHERE status = ? ORDER BY trigger_time ASC", (status_filter,))
        else:
            cursor.execute("SELECT * ORDER BY trigger_time ASC")
        return cursor.fetchall()

def get_active_reminders():
    """Используется фоновым потоком для поиска сработавших напоминаний."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, description FROM reminders WHERE trigger_time <= ? AND status = 'Ожидает'", (now_str,))
        return cursor.fetchall()
