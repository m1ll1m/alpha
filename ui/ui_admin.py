import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

def create_scrollable_frame(parent):
    # Создаем область со скроллингом
    canvas = tk.Canvas(parent, highlightthickness=0)
    scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    # Обновляем скролл-регион при изменении размера
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    
    # Автоматическая ширина
    def on_canvas_resize(e):
        canvas.itemconfig(canvas_window, width=e.width)

    canvas.bind("<Configure>", on_canvas_resize)
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    return scrollable_frame

# === ГЛАВНАЯ АДМИН-ПАНЕЛЬ ===

def draw_admin_screen(root, user_id, logout_callback):
    # Очищаем окно
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="Админ-панель", font=("Arial", 14, "bold"), pady=10).pack()

    # Кнопка выхода внизу
    bottom_panel = tk.Frame(root)
    bottom_panel.pack(side="bottom", fill="x", pady=10)
    tk.Button(bottom_panel, text="Выход", command=logout_callback, bg="#FADBD8", font=("Arial", 10, "bold"), pady=5, width=25).pack()

    # Вкладки для разных разделов
    tabs = ttk.Notebook(root)
    
    # Создаем вкладки
    users_tab = tk.Frame(tabs)
    products_tab = tk.Frame(tabs)
    orders_tab = tk.Frame(tabs)

    tabs.add(users_tab, text="Пользователи")
    tabs.add(products_tab, text="Товары")
    tabs.add(orders_tab, text="Заказы")
    
    tabs.pack(side="top", fill="both", expand=True, padx=10, pady=5)

    # ========== ВКЛАДКА: ПОЛЬЗОВАТЕЛИ ==========
    tk.Button(users_tab, text="Добавить", command=lambda: open_user_editor(), bg="#D4EFDF").pack(pady=10)
    users_list = create_scrollable_frame(users_tab)

    def refresh_users():
        # Очищаем и перестраиваем список
        for widget in users_list.winfo_children():
            widget.destroy()
        
        # Получаем всех пользователей
        conn = sqlite3.connect('store.db')
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, name, role, email FROM users")
        users = cursor.fetchall()
        conn.close()
        
        for user in users:
            user_id_col, name, role, email = user
            
            # Строка с информацией
            row = tk.Frame(users_list, pady=2, bd=1, relief="groove")
            row.pack(fill="x", padx=5, pady=2)
            
            tk.Label(row, text=f"ID:{user_id_col} | {name} [{role}]", anchor="w").pack(side="left", padx=5, expand=True, fill="x")
            
            # Кнопки действия
            tk.Button(row, text="📝", width=3, command=lambda u=user: open_user_editor(u)).pack(side="left", padx=2)
            
            tk.Button(row, text="❌", width=3, fg="red", command=lambda uid=user_id_col: delete_user(uid)).pack(side="left", padx=2)

    def open_user_editor(user_info=None):
        # Окно редактирования пользователя
        edit_window = tk.Toplevel(root)
        edit_window.title("Редактор")
        edit_window.geometry("350x550")
        
        current_id = user_info[0] if user_info else None
        initial_values = ["", "", "", "", "", ""]
        
        # Загружаем существующие данные
        if current_id:
            conn = sqlite3.connect('store.db')
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name, email, phone, password, delivery_address, role FROM users WHERE user_id=?",
                (current_id,)
            )
            result = cursor.fetchone()
            conn.close()
            if result:
                initial_values = list(result)
        
        # Создаем поля ввода
        field = {}
        # field_info = [
        #     ("Имя", "name"), ("Email", "email"), ("Телефон", "phone"),
        #     ("Пароль", "password"), ("Адрес", "address"), ("Роль", "role")
        # ]
        
        # for i, (label_text, key) in enumerate(field_info):
        #     tk.Label(edit_window, text=label_text).pack(pady=(5, 0))
        #     entry = tk.Entry(edit_window, width=30)
            
            # if key == "password":
            #     entry.config(show="*")
            
            # entry.insert(0, str(initial_values[i]))
            # entry.pack()
            # fields[key] = entry

        # Имя
        tk.Label(edit_window, text="Имя").pack(pady=(5,0))
        entry_name = tk.Entry(edit_window, width=30)
        entry_name.insert(0, initial_values[0])
        entry_name.pack()
        field["name"] = entry_name
    
    # Email
        tk.Label(edit_window, text="Email").pack(pady=(5,0))
        entry_email = tk.Entry(edit_window, width=30)
        entry_email.insert(0, initial_values[1])
        entry_email.pack()
        field["email"] = entry_email
    
    # Телефон
        tk.Label(edit_window, text="Телефон").pack(pady=(5,0))
        entry_phone = tk.Entry(edit_window, width=30)
        entry_phone.insert(0, initial_values[2])
        entry_phone.pack()
        field["phone"] = entry_phone
    
    # Пароль
        tk.Label(edit_window, text="Пароль").pack(pady=(5,0))
        entry_password = tk.Entry(edit_window, width=30, show="*")
        entry_password.insert(0, initial_values[3])
        entry_password.pack()
        field["password"] = entry_password
    
    # Адрес доставки
        tk.Label(edit_window, text="Адрес").pack(pady=(5,0))
        entry_address = tk.Entry(edit_window, width=30)
        entry_address.insert(0, initial_values[4])
        entry_address.pack()
        field["address"] = entry_address
    
    # Роль – теперь Combobox (фиксированный набор вариантов)
        tk.Label(edit_window, text="Роль").pack(pady=(5,0))
        role_var = tk.StringVar(value=initial_values[5])
        role_combo = ttk.Combobox(edit_window, textvariable=role_var, values=["user", "admin", "delivery"], state="readonly", width=27)
        role_combo.pack()
        field["role"] = role_combo
        
        def save_user():
            # Получаем и очищаем данные
            data = {key: field.get().strip() for key, field in field.items()}

            if not all(data.values()):
                    messagebox.showwarning("Внимание", "Заполните все поля!")
                    return
                
            if len(data['name']) < 3:
                    messagebox.showwarning("Ошибка", "Имя минимум 3 символа!")
                    return
                
            if "@" not in data['email'] or "." not in data['email']:
                    messagebox.showwarning('Ошибка', 'Email должен содержать "@" и "."!')
                    return
                
            if not data['phone'].isdigit():
                    messagebox.showwarning("Ошибка", "Телефон только цифры!")
                    return

            if len(data['password']) < 8:
                    messagebox.showwarning("Ошибка", "Пароль минимум 8 символов!")
                    return
                
            allowed_roles = ["user", "admin", "delivery"]
            if data['role'] not in allowed_roles:
                    messagebox.showwarning("Ошибка", "Роль должна быть user, admin или delivery!")
                    return

            # Проверяем валидность
            if current_id:
                # Обновляем существующего пользователя
                conn = sqlite3.connect('store.db')
                cursor = conn.cursor()
                
                cursor.execute(
                    "UPDATE users SET name=?, email=?, role=?, phone=?, password=?, delivery_address=? WHERE user_id=?",
                    (data['name'], data['email'], data['role'], data['phone'], data['password'], data['address'], current_id)
                )
                conn.commit()
                conn.close()
            else:
                # Добавляем нового пользователя
                conn = sqlite3.connect('store.db')
                cursor = conn.cursor()

                cursor.execute(
                    "INSERT INTO users (name, email, role, phone, password, delivery_address) VALUES (?,?,?,?,?,?)",
                    (data['name'], data['email'], data['role'], data['phone'], data['password'], data['address'])
                )
                conn.commit()
                conn.close()
                
            edit_window.destroy()
            refresh_users()
        
        tk.Button(edit_window, text="💾 Сохранить", bg="#D4EFDF", command=save_user, pady=8, width=15).pack(pady=20)

    def delete_user(user_id):
        # Удаляем пользователя
        if messagebox.askyesno("Удаление", "Удалить пользователя?"):
            conn = sqlite3.connect('store.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
            refresh_users()

    # ========== ВКЛАДКА: ТОВАРЫ ==========
    tk.Button(products_tab, text="Добавить товар", command=lambda: add_product_window(), bg="#D6EAF8").pack(pady=10)
    products_list = create_scrollable_frame(products_tab)

    def refresh_products():
        # Очищаем и перестраиваем список товаров
        for widget in products_list.winfo_children():
            widget.destroy()
        
        conn = sqlite3.connect('store.db')
        cursor = conn.cursor()
        cursor.execute("SELECT product_id, title, availability, price, category, description FROM products")
        items = cursor.fetchall()
        conn.close()

        for product in items:
            prod_id, title, stock, price, category, description = product
            
            # Информационная панель
            row = tk.Frame(products_list, pady=2, bd=1, relief="groove")
            row.pack(fill="x", padx=5, pady=2)
            
            info_text = f"[{category or '?'}] {title}\n{price} р. | Склад: {stock} шт."
            tk.Label(row, text=info_text, justify="left", anchor="w").pack(side="left", padx=5, expand=True, fill="x")
            
            # Кнопки управления
            tk.Button(row, text="📝", width=3, bg="#D6EAF8",command=lambda pid=prod_id, p=product: edit_product_window(pid, p)).pack(side="left", padx=1)
            
            tk.Button(row, text="❌", width=3, fg="red", command=lambda pid=prod_id: delete_product(pid)).pack(side="left", padx=5)

    def edit_product_window(prod_id, product_data):
        # Окно редактирования товара
        dialog = tk.Toplevel(root)
        dialog.title("Редактирование товара")
        dialog.geometry("300x520")
        
        prod_id, title, stock, price, category, description = product_data
        
        # Категория
        tk.Label(dialog, text="Категория:").pack()
        categories = ["Диваны", "Кресла", "Стулья", "Шкафы", "Тумбы", "Кровати", "Полки", "Столы", "Комоды"]
        category_combo = ttk.Combobox(dialog, values=categories, state="readonly")
        category_combo.set(category or "Диваны")
        category_combo.pack(pady=5)
        
        # Поля ввода
        fields = {}
        field_list = [
            ("Название", title),
            ("Цена", str(price)),
            ("Количество", str(stock))
        ]
        
        for field_name, value in field_list:
            tk.Label(dialog, text=field_name).pack()
            entry = tk.Entry(dialog, width=25)
            entry.insert(0, value)
            entry.pack()
            fields[field_name] = entry
        
        # Описание
        tk.Label(dialog, text="Описание").pack()
        text_widget = tk.Text(dialog, width=25, height=4)
        text_widget.insert("1.0", description or "")
        text_widget.pack()
        fields["Описание"] = text_widget

        def save_product():
            name = fields["Название"].get().strip()
            try:
                price_val = float(fields["Цена"].get().strip())
                qty_val = int(fields["Количество"].get().strip())
            except ValueError:
                messagebox.showerror("Ошибка", "Цена должна быть числом, количество - целое число!")
                return
            
            if price_val <= 0:
                messagebox.showerror("Ошибка", "Цена должна быть больше 0!")
                return
            
            if qty_val <= 0:
                messagebox.showerror("Ошибка", "Количество должно быть больше 0!")
                return

            if not name:
                messagebox.showwarning("Ошибка", "Заполните название!")
                return
            
            desc = fields["Описание"].get("1.0", "end-1c")
            
            conn = sqlite3.connect('store.db')
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE products SET title=?, price=?, availability=?, category=?, description=? WHERE product_id=?",
                (name, price_val, qty_val, category_combo.get(), desc, prod_id)
            )
            conn.commit()
            conn.close()
            dialog.destroy()
            refresh_products()
        
        tk.Button(dialog, text="Сохранить", bg="#D4EFDF", command=save_product, pady=8).pack(pady=10)
        
        tk.Button(dialog, text="Отмена", command=dialog.destroy, pady=5).pack()

    def delete_product(prod_id):
        # Удаляем товар
        if messagebox.askyesno("Удаление", "Удалить товар?"):
            conn = sqlite3.connect('store.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE product_id = ?", (prod_id,))
            conn.commit()
            conn.close()
            refresh_products()

    def add_product_window():
        # Окно добавления нового товара
        dialog = tk.Toplevel(root)
        dialog.title("Новый товар")
        dialog.geometry("300x420")
        
        # Категория
        tk.Label(dialog, text="Категория:").pack()
        categories = ["Диваны", "Кресла", "Стулья", "Шкафы", "Тумбы", "Кровати", "Полки", "Столы", "Комоды"]
        category_combo = ttk.Combobox(dialog, values=categories, state="readonly")
        category_combo.current(0)
        category_combo.pack(pady=5)
        
        # Поля ввода
        fields = {}
        field_list = ["Название", "Цена", "Количество", "Описание"]
        
        for field_name in field_list:
            tk.Label(dialog, text=field_name).pack()
            
            if field_name == "Описание":
                # Текстовое поле для описания
                text_widget = tk.Text(dialog, width=25, height=3)
                text_widget.pack()
                fields[field_name] = text_widget
            else:
                # Однострочное поле
                entry = tk.Entry(dialog, width=25)
                entry.pack()
                fields[field_name] = entry

        def save_product():
            name = fields["Название"].get()
            price = fields["Цена"].get()
            qty = fields["Количество"].get()
            desc = fields["Описание"].get("1.0", "end-1c")

            if not name or not price or not qty or not desc:
                messagebox.showwarning("Ошибка", "Заполните все поля!")
                return

            if len(name) < 3:
                messagebox.showwarning("Ошибка", "Название минимум 3 символа!")
                return

            try:
                price = float(price)
                qty = int(qty)
            except ValueError:
                messagebox.showerror("Ошибка", "Цена должна быть числом, количество - целое число!")
                return
            
            if len(desc) < 3:
                messagebox.showwarning("Ошибка", "Описание минимум 3 символа!")
                return
            
            if name and price and qty:
                conn = sqlite3.connect('store.db')
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO products (title, price, availability, category, description) VALUES (?,?,?,?,?)",
                    (name, price, qty, category_combo.get(), desc)
                )
                conn.commit()
                conn.close()
                messagebox.showinfo("Успех", "Товар добавлен!")
                dialog.destroy()
                refresh_products()
        
        tk.Button(dialog, text="✅ Добавить", bg="#D6EAF8", command=save_product).pack(pady=10)

    # ========== ВКЛАДКА: ЗАКАЗЫ ==========
    tk.Button(orders_tab, text="🔄 Обновить", command=lambda: refresh_orders()).pack(pady=10)
    orders_list = create_scrollable_frame(orders_tab)
    
    def refresh_orders():
        # Очищаем и перестраиваем список заказов
        for widget in orders_list.winfo_children():
            widget.destroy()
        
        # Получаем все заказы
        conn = sqlite3.connect('store.db')
        cursor = conn.cursor()
        cursor.execute(
            """SELECT o.order_id, u.name, u.phone, o.delivery_address, o.delivery_status 
            FROM orders o 
            JOIN users u ON o.user_id = u.user_id 
            ORDER BY o.order_id DESC""")
        orders = cursor.fetchall()
        conn.close()

        # Маппинг статусов
        status_names = {
            "0": "Оплачено",
            "1": "Принят",
            "2": "В пути",
            "3": "Доставлен"
        }
        
        for order in orders:
            order_id, customer_name, phone, address, status = order
            status_text = status_names.get(str(status), status)
            
            # Получаем товары в заказе
            conn = sqlite3.connect('store.db')
            cursor = conn.cursor()
            cursor.execute(
                """SELECT p.title, oi.amount, oi.price 
                   FROM order_items oi 
                   JOIN products p ON oi.product_id = p.product_id 
                   WHERE oi.order_id = ?""",
                (order_id,)
            )
            items = cursor.fetchall()
            conn.close()

            # Формируем текст с товарами
            items_text = ""
            for item_title, item_amount, item_price in items:
                item_total = item_amount * item_price
                items_text += f"  • {item_title}: {item_amount} шт. × {item_price} р. = {item_total} р.\n"
            
            # Карточка заказа
            card_text = (f"Заказ #{order_id} | {customer_name} (тел. {phone}) | {status_text}\n"
                        f"{address}\n\n"
                        f"Товары:\n{items_text}")
            
            tk.Label(orders_list, text=card_text.strip(), justify="left", relief="groove", bd=1, pady=5, anchor="w").pack(fill="x", pady=2, padx=5)

    # === ПЕРВИЧНАЯ ЗАГРУЗКА ===
    refresh_users()
    refresh_products()
    refresh_orders()