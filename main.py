import tkinter as tk
from tkinter import ttk, messagebox
import database
import notifications

class ReminderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Напоминалка Windows 11")
        self.root.geometry("750x450")
        
        # Поля ввода
        frame_input = tk.LabelFrame(root, text="Новое напоминание", padx=10, pady=10)
        frame_input.pack(fill="x", padx=10, pady=5)
        
        tk.Label(frame_input, text="Заголовок:").grid(row=0, column=0, sticky="w")
        self.entry_title = tk.Entry(frame_input, width=30)
        self.entry_title.grid(row=0, column=1, padx=5, pady=2)
        
        tk.Label(frame_input, text="Описание:").grid(row=1, column=0, sticky="w")
        self.entry_desc = tk.Entry(frame_input, width=30)
        self.entry_desc.grid(row=1, column=1, padx=5, pady=2)
        
        tk.Label(frame_input, text="Дата и время (ГГГГ-ММ-ДД ЧЧ:ММ):").grid(row=2, column=0, sticky="w")
        self.entry_time = tk.Entry(frame_input, width=30)
        self.entry_time.grid(row=2, column=1, padx=5, pady=2)
        
        btn_add = tk.Button(frame_input, text="Добавить", command=self.add_reminder)
        btn_add.grid(row=3, column=1, pady=5, sticky="e")
        
        # Фильтр статусов
        frame_filter = tk.Frame(root)
        frame_filter.pack(fill="x", padx=10, pady=5)
        
        tk.Label(frame_filter, text="Фильтр по статусу:").pack(side="left")
        self.combo_filter = ttk.Combobox(frame_filter, values=["Все", "Ожидает", "Готово", "Просрочено", "Отменено"], state="readonly")
        self.combo_filter.set("Все")
        self.combo_filter.pack(side="left", padx=5)
        self.combo_filter.bind("<<ComboboxSelected>>", lambda e: self.load_data())
        
        # Таблица напоминаний
        self.tree = ttk.Treeview(root, columns=("id", "title", "desc", "time", "status"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Заголовок")
        self.tree.heading("desc", text="Описание")
        self.tree.heading("time", text="Время срабатывания")
        self.tree.heading("status", text="Статус")
        
        self.tree.column("id", width=30)
        self.tree.column("title", width=150)
        self.tree.column("desc", width=250)
        self.tree.column("time", width=130)
        self.tree.column("status", width=100)
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Кнопки управления
        frame_buttons = tk.Frame(root)
        frame_buttons.pack(fill="x", padx=10, pady=5)
        
        tk.Button(frame_buttons, text="Отметить как 'Готово'", command=lambda: self.change_status("Готово")).pack(side="left", padx=2)
        tk.Button(frame_buttons, text="Отметить как 'Отменено'", command=lambda: self.change_status("Отменено")).pack(side="left", padx=2)
        tk.Button(frame_buttons, text="Удалить", command=self.delete_reminder, fg="red").pack(side="right", padx=2)
        
        self.load_data()

    def load_data(self):
        """Загружает данные из БД в таблицу интерфейса."""
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        f = self.combo_filter.get()
        for row in database.get_reminders(f):
            self.tree.insert("", "end", values=row)

    def add_reminder(self):
        title = self.entry_title.get().strip()
        desc = self.entry_desc.get().strip()
        r_time = self.entry_time.get().strip()
        
        if not title or not r_time:
            messagebox.showwarning("Ошибка", "Заполните Заголовок и Время!")
            return
        
        try:
            # Проверка формата времени
            from datetime import datetime
            datetime.strptime(r_time, "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат времени! Используйте: ГГГГ-ММ-ДД ЧЧ:ММ")
            return
            
        database.add_reminder(title, desc, r_time)
        self.load_data()
        self.entry_title.delete(0, tk.END)
        self.entry_desc.delete(0, tk.END)
        self.entry_time.delete(0, tk.END)

    def get_selected_id(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите напоминание из списка!")
            return None
        return self.tree.item(selected[0])['values'][0]

    def change_status(self, status):
        rem_id = self.get_selected_id()
        if rem_id:
            database.update_status(rem_id, status)
            self.load_data()

    def delete_reminder(self):
        rem_id = self.get_selected_id()
        if rem_id:
            database.delete_reminder(rem_id)
            self.load_data()

if __name__ == "__main__":
    database.init_db()  # Шаг 1: инициализация БД
    notifications.start_notification_thread()  # Шаг 2: запуск фонового трекера фоном
    
    root = tk.Tk()
    app = ReminderApp(root)
    root.mainloop()