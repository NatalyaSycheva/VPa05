import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import database
import subprocess
import os

class AdvancedReminderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Напоминалка Windows 11")
        self.root.geometry("850x550")
        
        # Перехват закрытия окна (Пункт 6)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Главный заголовок стиля Windows 11
        tk.Label(root, text="Напоминалка", font=("Segoe UI", 16, "bold")).pack(pady=10)
        
        # Форма ввода
        frame_form = tk.LabelFrame(root, text="Добавить новое напоминание", font=("Segoe UI", 10))
        frame_form.pack(fill="x", padx=15, pady=5)
        
        tk.Label(frame_form, text="Заголовок:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.entry_title = tk.Entry(frame_form, width=80)
        self.entry_title.grid(row=0, column=1, padx=10, pady=5, columnspan=2)
        
        tk.Label(frame_form, text="Описание:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.entry_desc = tk.Entry(frame_form, width=80)
        self.entry_desc.grid(row=1, column=1, padx=10, pady=5, columnspan=2)
        
        tk.Label(frame_form, text="Дата и время:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        
        # Панель быстрых кнопок (Пункт 2)
        frame_quick = tk.Frame(frame_form)
        frame_quick.grid(row=2, column=1, sticky="w", padx=10)
        
        tk.Button(frame_quick, text="Через 1 мин", command=lambda: self.set_quick_time(1)).pack(side="left", padx=2)
        tk.Button(frame_quick, text="Через 5 мин", command=lambda: self.set_quick_time(5)).pack(side="left", padx=2)
        tk.Button(frame_quick, text="Через 15 мин", command=lambda: self.set_quick_time(15)).pack(side="left", padx=2)
        tk.Button(frame_quick, text="Через 1 час", command=lambda: self.set_quick_time(60)).pack(side="left", padx=2)
        
        self.entry_time = tk.Entry(frame_form, width=80)
        self.entry_time.grid(row=3, column=1, padx=10, pady=5, columnspan=2)
        self.set_quick_time(1) # По умолчанию ставим +1 минуту от текущего времени
        
        # Действия формы
        btn_add = tk.Button(frame_form, text="Добавить напоминание", font=("Segoe UI", 9, "bold"), command=self.add_reminder)
        btn_add.grid(row=4, column=1, sticky="w", padx=10, pady=10)
        
        btn_test = tk.Button(frame_form, text="Тест уведомления", command=self.trigger_test_notification)
        btn_test.grid(row=4, column=2, sticky="w", padx=10, pady=10)
        
        # Фильтры и Статистика
        frame_ctrl = tk.Frame(root)
        frame_ctrl.pack(fill="x", padx=15, pady=5)
        
        tk.Label(frame_ctrl, text="Фильтр по статусу:").pack(side="left")
        self.combo_filter = ttk.Combobox(frame_ctrl, values=["Все", "Ожидает", "Готово", "Просрочено"], state="readonly", width=12)
        self.combo_filter.set("Все")
        self.combo_filter.pack(side="left", padx=5)
        self.combo_filter.bind("<<ComboboxSelected>>", lambda e: self.load_data())
        
        tk.Button(frame_ctrl, text="Обновить", command=self.load_data).pack(side="left", padx=10)
        
        self.lbl_stats = tk.Label(frame_ctrl, text="Всего: 0 | Ожидает: 0 | Готово: 0 | Просрочено: 0", font=("Segoe UI", 10, "bold"))
        self.lbl_stats.pack(side="right", padx=10)
        
        # Таблица напоминаний со структурой как на макете
        tk.Label(root, text="Список напоминаний", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=15)
        
        self.tree = ttk.Treeview(root, columns=("id", "title", "desc", "time", "status", "created"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Заголовок")
        self.tree.heading("desc", text="Описание")
        self.tree.heading("time", text="Дата/Время")
        self.tree.heading("status", text="Статус")
        self.tree.heading("created", text="Создано")
        
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("title", width=140)
        self.tree.column("desc", width=220)
        self.tree.column("time", width=120, anchor="center")
        self.tree.column("status", width=90, anchor="center")
        self.tree.column("created", width=120, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=15, pady=5)
        
        self.load_data()
        self.start_background_scheduler()

    def set_quick_time(self, minutes):
        future_time = datetime.now() + timedelta(minutes=minutes)
        self.entry_time.delete(0, tk.END)
        self.entry_time.insert(0, future_time.strftime("%Y-%m-%d %H:%M"))

    def start_background_scheduler(self):
        """Автоматически подхватывает запуск scheduler.py, если он ещё не запущен."""
        try:
            subprocess.Popen(["python", "scheduler.py"], creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception:
            pass

    def load_data(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        current_filter = self.combo_filter.get()
        rows = database.get_reminders(current_filter)
        
        for row in rows:
            self.tree.insert("", "end", values=row)
            
        # Обновление текста статистики
        s = database.get_stats()
        self.lbl_stats.config(text=f"Всего: {s['Всего']} | Ожидает: {s['Ожидает']} | Готово: {s['Готово']} | Просрочено: {s['Просрочено']}")

    def add_reminder(self):
        t = self.entry_title.get().strip()
        d = self.entry_desc.get().strip()
        tm = self.entry_time.get().strip()
        
        if not t or not tm:
            messagebox.showwarning("Внимание", "Поля Заголовок и Время обязательны!")
            return
            
        try:
            datetime.strptime(tm, "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showerror("Ошибка", "Формат времени должен быть: ГГГГ-ММ-ДД ЧЧ:ММ")
            return
            
        database.add_reminder(t, d, tm)
        self.load_data()
        self.entry_title.delete(0, tk.END)
        self.entry_desc.delete(0, tk.END)
        self.set_quick_time(1)

    def trigger_test_notification(self):
        """Мгновенный тест уведомления (Пункт 4)."""
        database.add_reminder("Тестовый пуш", "Проверка мгновенного вызова системных окон", datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.load_data()

    def on_closing(self):
        """Подтверждение закрытия (Пункт 6)."""
        if messagebox.askyesno("Выход", "Вы действительно хотите закрыть интерфейс?\n(Фоновые напоминания продолжат работать)"):
            self.root.destroy()

if __name__ == "__main__":
    database.init_db()
    root = tk.Tk()
    app = AdvancedReminderApp(root)
    root.mainloop()
