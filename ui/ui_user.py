import tkinter as tk
from tkinter import messagebox, ttk
import cart_manager, ui.ui_cart as ui_cart
import sqlite3

def draw_user_screen(root, user_id, logout_callback):
    # Очищаем окно
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="Каталог мебели ALPHA", font=("Arial", 16, "bold")).pack(pady=10)

    # === ПАНЕЛЬ ФИЛЬТРОВ ===
    filter_frame = tk.Frame(root)
    filter_frame.pack(pady=10, fill="x", padx=20)

    # Фильтр по названию товара
    tk.Label(filter_frame, text="Модель:").pack(side="left")
    search_entry = tk.Entry(filter_frame, width=20)
    search_entry.pack(side="left", padx=(5, 15))
    
    # Фильтр по категории
    tk.Label(filter_frame, text="Категория:").pack(side="left")
    categories = ["Все", "Диваны", "Кресла", "Стулья", "Шкафы", "Тумбы", "Кровати", "Полки", "Столы", "Комоды"]
    category_combo = ttk.Combobox(filter_frame, values=categories, state="readonly", width=15)
    category_combo.current(0)  # По умолчанию "Все"
    category_combo.pack(side="left", padx=5)

    # === НИЖНЯЯ ПАНЕЛЬ (кнопки) ===
    bottom_frame = tk.Frame(root)
    bottom_frame.pack(side="bottom", fill="x", pady=10)
    
    tk.Button(bottom_frame, text="Выйти", command=logout_callback, width=10).pack(side="right", padx=20)
    
    # Кнопка корзины
    tk.Button(bottom_frame, text="Корзина", bg="yellow", font=("Arial", 10, "bold"),command=lambda: ui_cart.draw_cart_screen(root, user_id, lambda: draw_user_screen(root, user_id, logout_callback))).pack(side="left", padx=20)
    
    # Кнопка сброса фильтров
    def clear_filters():
        search_entry.delete(0, 'end')
        category_combo.current(0)
        refresh_products()
    
    tk.Button(bottom_frame, text="Сбросить", command=clear_filters).pack(side="left")

    # === СПИСОК ТОВАРОВ СО СКРОЛЛОМ ===
    canvas = tk.Canvas(root, highlightthickness=0)
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    products_frame = tk.Frame(canvas)

    # Функция для автоматической ширины скролл-области
    def on_canvas_resize(e):
        canvas.itemconfig(canvas_window, width=e.width)

    canvas_window = canvas.create_window((0, 0), window=products_frame, anchor="nw")
    canvas.bind("<Configure>", on_canvas_resize)
    products_frame.bind("<Configure>", 
        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True, padx=20)
    scrollbar.pack(side="right", fill="y")

    # Загружаем корзину пользователя
    user_cart = cart_manager.load_cart(user_id)

    def add_to_cart(prod_id, product_title, product_price, stock_qty):
        # Проверяем наличие товара
        if stock_qty <= 0:
            messagebox.showerror("Ошибка", "Товара нет в наличии!")
            return
        
        prod_id = str(prod_id)
        
        # Если товар уже в корзине, увеличиваем количество
        if prod_id in user_cart:
            if user_cart[prod_id]['amount'] + 1 > stock_qty:
                messagebox.showwarning("Внимание", "Лимит склада!")
                return
            user_cart[prod_id]['amount'] += 1
        else:
            # Добавляем новый товар
            user_cart[prod_id] = {
                'title': product_title, 
                'price': product_price, 
                'amount': 1
            }
        
        # Сохраняем корзину
        cart_manager.save_cart(user_id, user_cart)
        messagebox.showinfo("Корзина", f"{product_title} добавлен!")

    def refresh_products(event=None):
        # Удаляем все товары (для перестроения списка)
        for widget in products_frame.winfo_children():
            widget.destroy()
        
        # Получаем значения фильтров
        search_text = search_entry.get().strip().lower()
        selected_category = category_combo.get()

        try:
            # Загружаем все товары из БД
            conn = sqlite3.connect('store.db')
            cursor = conn.cursor()
            cursor.execute("SELECT product_id, title, category, price, availability FROM products")
            all_products = cursor.fetchall()
            conn.close()
            
            # Фильтруем по названию и категории
            filtered_products = []
            for product in all_products:
                prod_id, title, category, price, qty = product
                
                # Проверяем совпадение названия
                matches_name = search_text in title.lower()
                
                # Проверяем совпадение категории
                matches_category = (selected_category == "Все") or (category == selected_category)
                
                if matches_name and matches_category:
                    filtered_products.append(product)

            # Если ничего не найдено
            if not filtered_products:
                tk.Label(products_frame, text="Товары не найдены", 
                        fg="gray", font=("Arial", 11)).pack(pady=30)
                return

            # Выводим каждый товар
            for product in filtered_products:
                prod_id, title, category, price, qty = product
                
                # Создаем блок товара
                item_card = tk.Frame(products_frame, bd=1, relief="groove", pady=10, padx=15)
                item_card.pack(fill="x", pady=5, padx=5)
                
                # Левая часть (информация)
                info_section = tk.Frame(item_card)
                info_section.pack(side="left", fill="both", expand=True)
                
                # Название товара
                tk.Label(info_section, text=title, font=("Arial", 11, "bold"), justify="left").pack(anchor="w")
                
                # Категория и цена
                tk.Label(info_section, text=f"Категория: {category}  |  Цена: {price} руб.", fg="#555555").pack(anchor="w")
                
                # Статус наличия
                if qty > 0:
                    status_text = "● В наличии"
                    status_color = "green"
                else:
                    status_text = "○ Нет в наличии"
                    status_color = "red"
                
                tk.Label(info_section, text=status_text, fg=status_color, 
                        font=("Arial", 9, "bold")).pack(anchor="w")
                
                # Правая часть (кнопка)
                if qty > 0:
                    button_color = "lightgreen"
                    button_state = "normal"
                else:
                    button_color = "#eeeeee"
                    button_state = "disabled"
                
                tk.Button(item_card, text="В корзину", bg=button_color, width=12, state=button_state,command=lambda pid=prod_id, t=title, p=price, q=qty: add_to_cart(pid, t, p, q)).pack(side="right", padx=10)
                          
        except Exception as error:
            messagebox.showerror("Ошибка", f"Ошибка БД: {error}")

    # === ОБРАБОТЧИКИ СОБЫТИЙ ===
    # Кнопка поиска
    tk.Button(filter_frame, text="Найти", command=refresh_products, 
              bg="orange", width=8).pack(side="left", padx=5)
    
    # Поиск при выборе категории
    category_combo.bind("<<ComboboxSelected>>", refresh_products)
    
    # Поиск при нажатии Enter в поле поиска
    search_entry.bind('<Return>', lambda e: refresh_products())

    # Загружаем и показываем товары сразу
    refresh_products()