import tkinter as tk
from tkinter import messagebox
import sqlite3, cart_manager
from datetime import datetime

def draw_payment_screen(root, user_id, address, total_sum, cart, success_callback):
    # Очищаем окно
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="💳 Оплата банковской картой", font=("Arial", 14, "bold"), pady=20).pack()
    
    # Контейнер формы оплаты
    form = tk.Frame(root, padx=20, pady=20, relief="groove", bd=2)
    form.pack(pady=10)

    # Показываем сумму к оплате
    tk.Label(form, text=f"Сумма: {total_sum} руб.", font=("Arial", 11, "bold"), fg="green").pack(pady=10)
    
    # Поле номера карты
    tk.Label(form, text="Номер карты (16 цифр):").pack(anchor="w")
    card_entry = tk.Entry(form, width=30)
    card_entry.insert(0, "4400 0000 0000 0000")
    card_entry.pack(pady=5)

    # Контейнер для срока и CVV
    card_details = tk.Frame(form)
    card_details.pack(fill="x", pady=10)

    # Поле срока действия
    expiry_frame = tk.Frame(card_details)
    expiry_frame.pack(side="left", padx=(0, 20))
    tk.Label(expiry_frame, text="Срок (MM/YY):").pack(anchor="w")
    date_entry = tk.Entry(expiry_frame, width=10)
    date_entry.insert(0, "12/26")
    date_entry.pack()

    # Поле CVV
    cvv_frame = tk.Frame(card_details)
    cvv_frame.pack(side="left")
    tk.Label(cvv_frame, text="CVV:").pack(anchor="w")
    cvv_entry = tk.Entry(cvv_frame, width=8, show="*")
    cvv_entry.insert(0, "123")
    cvv_entry.pack()

    def confirm_payment():
        # Получаем значения
        card_num = card_entry.get().replace(" ", "")
        date = date_entry.get().strip()
        cvv = cvv_entry.get().strip()

        # Проверяем номер карты
        if len(card_num) != 16 or not card_num.isdigit():
            messagebox.showerror("Ошибка", "Номер карты должен быть 16 цифр!")
            return
        
        # Проверяем срок (формат MM/YY)
        if "/" not in date or len(date) != 5:
            messagebox.showerror("Ошибка", "Срок в формате MM/YY (например, 12/26)!")
            return
        
        # Проверяем CVV
        if len(cvv) != 3 or not cvv.isdigit():
            messagebox.showerror("Ошибка", "CVV должен быть 3 цифры!")
            return

        try:
            # Получаем текущее время
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Создаем новый заказ (статус "0" = Оплачено)
            conn = sqlite3.connect('store.db')
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO orders (user_id, delivery_status, delivery_address, created_at) VALUES (?, ?, ?, ?)",
                (user_id, "0", address, now)
            )
            order_id = cursor.lastrowid
            conn.commit()
            conn.close()

            # Добавляем товары заказа и уменьшаем остаток на складе
            for product_id, info in cart.items():
                # Добавляем товар в таблицу order_items
                conn = sqlite3.connect('store.db')
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO order_items (order_id, product_id, amount, price) VALUES (?, ?, ?, ?)",
                    (order_id, product_id, info['amount'], info['price'])
                )
                conn.commit()
                conn.close()
                
                # Уменьшаем количество на складе
                conn = sqlite3.connect('store.db')
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE products SET availability = availability - ? WHERE product_id = ?",
                    (info['amount'], product_id)
                )
                conn.commit()
                conn.close()

            # Записываем информацию о платеже
            conn = sqlite3.connect('store.db')
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO payments (order_id, total_price, status) VALUES (?, ?, 'Успешно')",
                (order_id, total_sum)
            )
            conn.commit()
            conn.close()

            # Очищаем корзину
            cart_manager.save_cart(user_id, {})
            
            messagebox.showinfo("Успех", f"Оплата принята!\nНомер заказа: {order_id}")
            success_callback()  # Возвращаемся в каталог

        except Exception as error:
            messagebox.showerror("Ошибка", f"Не удалось оформить заказ: {error}")

    # Кнопки управления
    tk.Button(root, text="💳 Подтвердить оплату", bg="#D4EFDF", font=("Arial", 10, "bold"), command=confirm_payment, pady=10, width=25).pack(pady=10)
    
    tk.Button(root, text="❌ Отмена", command=success_callback, fg="red").pack()