import tkinter as tk
from tkinter import messagebox
import threading
import time
import database

def show_popup(title, description, reminder_id):
    """Создает независимое окно поверх всех остальных."""
    root = tk.Tk()
    root.withdraw()  # Скрываем основное мелкое окно tk
    root.attributes("-topmost", True)  # Выводим на передний план
    
    # Текст сообщения
    msg = f"Напоминание: {title}\n\nОписание: {description}\n\nОтметить как выполнено?"
    answer = messagebox.askyesno("Сработало напоминание!", msg, parent=root)
    
    # Если пользователь нажал 'Да', меняем статус на 'Готово'
    if answer:
        database.update_status(reminder_id, "Готово")
    else:
        database.update_status(reminder_id, "Просрочено")
        
    root.destroy()

def check_loop():
    """Фоновый цикл проверки времени каждую минуту."""
    while True:
        database.check_overdue()
        triggered = database.get_active_reminders()
        
        for rem_id, title, desc in triggered:
            # Запускаем всплывающее окно в отдельном потоке, чтобы не вешать программу
            threading.Thread(target=show_popup, args=(title, desc, rem_id), daemon=True).start()
            
        time.sleep(30)  # Проверка каждые 30 секунд

def start_notification_thread():
    """Запускает фоновый мониторинг."""
    t = threading.Thread(target=check_loop, daemon=True)
    t.start()
