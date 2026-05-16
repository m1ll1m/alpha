import tkinter as tk
from tkinter import messagebox
import sqlite3
import cart_manager, ui.ui_payment as ui_payment

def draw_cart_screen(root, user_id, back_callback):
    # Очищаем окно
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="🛒 Ваша корзина", font=("Arial", 16, "bold")).pack(pady=10)

    # Загружаем корзину из файла
    cart = cart_manager.load_cart(user_id)
    
    # Если корзина пуста
    if not cart:
        tk.Label(root, text="Корзина пуста", fg="gray", font=("Arial", 11)).pack(pady=30)
        tk.Button(root, text="Назад в каталог", command=back_callback).pack()
        return

    # Показываем товары в корзине
    items_frame = tk.Frame(root)
    items_frame.pack(pady=10, fill="both", expand=True, padx=20)

    # Считаем общую сумму
    total_sum = 0
    for product_id, info in cart.items():
        item_total = info['price'] * info['amount']
        total_sum += item_total
        item_text = f"• {info['title']} ({info['amount']} шт.) — {item_total} руб."
        tk.Label(items_frame, text=item_text, anchor="w").pack(fill="x", pady=2)

    # Показываем итоговую сумму
    tk.Label(root, text=f"ИТОГО: {total_sum} руб.", font=("Arial", 12, "bold"), fg="darkgreen").pack(pady=10)

    # Поле для ввода адреса доставки
    tk.Label(root, text="Адрес доставки:").pack()
    address_entry = tk.Entry(root, width=45)
    
    # Подтягиваем адрес из профиля пользователя
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()
    cursor.execute("SELECT delivery_address FROM users WHERE user_id = ?", (user_id,))
    user_data = cursor.fetchone()
    conn.close()

    if user_data and user_data[0]:
        address_entry.insert(0, user_data[0])
    address_entry.pack(pady=5)

    def start_payment():
        # Переход к оплате
        address = address_entry.get().strip()
        if not address:
            messagebox.showwarning("Внимание", "Введите адрес доставки!")
            return

        # Переходим на экран оплаты
        ui_payment.draw_payment_screen(
            root, user_id, address, total_sum, cart, back_callback
        )

    # Кнопки управления
    button_frame = tk.Frame(root)
    button_frame.pack(pady=20)
    
    tk.Button(button_frame, text="Перейти к оплате", bg="#aaffaa", font=("Arial", 10, "bold"), command=start_payment).pack(side="left", padx=10)
    
    tk.Button(button_frame, text="Назад", command=back_callback).pack(side="left")