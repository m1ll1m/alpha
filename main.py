import tkinter as tk
from tkinter import messagebox
import sqlite3
import ui.ui_user as ui_user, ui.ui_admin as ui_admin, ui.ui_delivery as ui_delivery

# Создание главного окна приложения
root = tk.Tk()
root.title("Магазин мебели")
root.geometry("600x600")

def draw_auth():
    # Очищаем окно от всех элементов
    for widget in root.winfo_children():
        widget.destroy()
    
    # Заголовок экрана авторизации
    tk.Label(root, text="Авторизация", font=("Arial", 18)).pack(pady=20)
    
    # Поле для ввода Email
    tk.Label(root, text="Email:").pack()
    email_entry = tk.Entry(root)
    email_entry.pack(pady=5)
    
    # Поле для ввода пароля (скрывается звездочками)
    tk.Label(root, text="Пароль:").pack()
    password_entry = tk.Entry(root, show="*")
    password_entry.pack(pady=5)

    def go_login():
        # Проверяем данные в базе
        conn = sqlite3.connect('store.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, role FROM users WHERE email=? AND password=?",
            (email_entry.get(), password_entry.get())
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            user_id, role = user
            # Переходим в нужный раздел в зависимости от роли
            if role == 'admin':
                ui_admin.draw_admin_screen(root, user_id, draw_auth)
            elif role == 'delivery':
                ui_delivery.draw_delivery_screen(root, user_id, draw_auth)
            else:
                ui_user.draw_user_screen(root, user_id, draw_auth)
        else:
            messagebox.showerror("Ошибка", "Неверный email или пароль!")

    tk.Button(root, text="Войти", command=go_login, bg="lightblue").pack(pady=10)
    tk.Button(root, text="Регистрация", command=draw_reg).pack()

def draw_reg():
    # Очищаем окно
    for widget in root.winfo_children():
        widget.destroy()
    
    tk.Label(root, text="Регистрация", font=("Arial", 18)).pack(pady=10)
    
    # Создаем поля для ввода
    fields = ["Имя", "Email", "Телефон", "Пароль", "Адрес"]
    entries = {}
    
    for field_name in fields:
        tk.Label(root, text=field_name).pack()
        entry = tk.Entry(root)
        if field_name == "Пароль":
            entry.config(show="*")  # Скрываем пароль
        entry.pack()
        entries[field_name] = entry

    def save_reg():
        # Получаем и очищаем значения от пробелов
        data = {field: entry.get().strip() for field, entry in entries.items()}
        
        # Проверка заполнения всех полей
        if not all(data.values()):
            messagebox.showwarning("Внимание", "Заполните все поля!")
            return

        # Валидация имени
        if len(data["Имя"]) < 3:
            messagebox.showwarning("Ошибка", "Имя должно быть минимум 3 символа!")
            return

        # Валидация email
        if "@" not in data["Email"]:
            messagebox.showwarning("Ошибка", "Email должен содержать @!")
            return

        # Валидация телефона (только цифры и плюс в начале)
        phone_clean = data["Телефон"].replace("+", "")
        if not phone_clean.isdigit():
            messagebox.showwarning("Ошибка", "Телефон должен содержать только цифры!")
            return

        # Валидация пароля
        if len(data["Пароль"]) < 8:
            messagebox.showwarning("Ошибка", "Пароль минимум 8 символов!")
            return

        # Валидация адреса (не должен быть только числами)
        if data["Адрес"].isdigit():
            messagebox.showwarning("Ошибка", "Адрес не может быть только цифрами!")
            return

        # Сохраняем нового пользователя в БД
        try:
            conn = sqlite3.connect('store.db')
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, email, phone, password, delivery_address, role) VALUES (?, ?, ?, ?, ?, 'user')",
                [data["Имя"], data["Email"], data["Телефон"], data["Пароль"], data["Адрес"]]
            )
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Успех", "Регистрация завершена, можете войти в окне авторизации!")
            draw_auth()
        except sqlite3.IntegrityError:
            messagebox.showerror("Ошибка", "Пользователь с таким email уже существует!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при регистрации: {str(e)}")

    tk.Button(root, text="Создать", command=save_reg, bg="lightgreen").pack(pady=10)
    tk.Button(root, text="Назад", command=draw_auth).pack()

# Запуск приложения - показываем экран авторизации
draw_auth()
# Запускаем главный цикл обработки событий
root.mainloop()