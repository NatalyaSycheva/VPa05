import time
import tkinter as tk
from tkinter import messagebox
from win11toast import toast
import database

def show_double_notification(rem_id, title, desc):
    # 1. Отправка системного Windows 11 Toast
    try:
        toast(title, f"Сработало напоминание!\n{desc}", duration='long')
    except Exception:
        pass # Защита, если библиотека не поддерживается на старых ОС

    # 2. Показ Pop-up окна поверх всех окон
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    messagebox.showinfo(f"Напоминание: {title}", f"Описание: {desc}", parent=root)
    root.destroy()

    # 3. Автоматический перевод в статус «Готово» после показа
    database.set_status(rem_id, "Готово")

def main_loop():
    database.init_db()
    while True:
        due = database.get_due_reminders()
        for rem_id, title, desc in due:
            show_double_notification(rem_id, title, desc)
        time.sleep(20) # Проверка базы данных три раза в минуту

if __name__ == "__main__":
    main_loop()
