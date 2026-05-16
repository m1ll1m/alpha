import tkinter as tk
from tkinter import messagebox
import sqlite3

def draw_delivery_screen(root, user_id, logout_callback):
    # Очищаем окно
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="Панель доставки", font=("Arial", 16, "bold"), pady=15).pack()

    # Контейнер для списка заказов
    orders_list = tk.Frame(root)
    orders_list.pack(fill="both", expand=True, padx=15)

    def show_earnings():
        # Показываем статистику заработков
        try:
            # Считаем количество доставленных заказов
            conn = sqlite3.connect('store.db')
            cursor = conn.cursor()
            cursor.execute(
                """SELECT COUNT(order_id) FROM orders WHERE courier_id = ? AND delivery_status = '3'""",
                (user_id,)
            )
            result = cursor.fetchall()
            conn.close()

            delivered_count = result[0][0] if result and result[0][0] else 0
            rate_per_order = 400
            total_earned = delivered_count * rate_per_order

            message = (
                f"Ваша статистика:\n\n"
                f"Доставлено: {delivered_count}\n"
                f"Ставка: {rate_per_order} руб./заказ\n"
                f"Итого: {total_earned} руб."
            )
            messagebox.showinfo("Заработок", message)
        except Exception as error:
            messagebox.showerror("Ошибка", f"Не удалось расчитать: {error}")

    def has_active_order(courier_id):
        # Проверяем, есть ли у курьера активный заказ (не завершённый)
        conn = sqlite3.connect('store.db')
        cursor = conn.cursor()
        cursor.execute(
            """SELECT COUNT(order_id) FROM orders WHERE courier_id = ? AND delivery_status != '3' AND delivery_status IS NOT NULL""", (courier_id,)
        )
        result = cursor.fetchall()
        conn.close()
        return result[0][0] > 0 if result else False

    def update_order_status(order_id, new_status):
        # Обновляем статус заказа
        try:
            # Если курьер принимает новый заказ (статус "1"), проверяем ограничение
            if new_status == "1":
                if has_active_order(user_id):
                    messagebox.showwarning("Ограничение", "Вы можете взять только один заказ!\nЗавершите текущий заказ перед тем как взять новый.")
                    return
            
            conn = sqlite3.connect('store.db')
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE orders SET delivery_status = ?, courier_id = ? WHERE order_id = ?",
                (new_status, user_id, order_id)
            )
            conn.commit()
            conn.close()
            refresh_orders()
        except Exception as error:
            messagebox.showerror("Ошибка", f"Ошибка обновления: {error}")

    def refresh_orders():
        # Очищаем и перестраиваем список заказов
        for widget in orders_list.winfo_children():
            widget.destroy()

        # Получаем свободные заказы и заказы курьера
        conn = sqlite3.connect('store.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.order_id, u.name, u.phone, o.delivery_address, o.delivery_status, o.courier_id
            FROM orders o
            JOIN users u ON o.user_id = u.user_id
            WHERE (o.delivery_status != '3' AND o.delivery_status IS NOT NULL)
            AND (o.courier_id IS NULL OR o.courier_id = ?)
            ORDER BY o.order_id DESC
        """, (user_id,))
        orders = cursor.fetchall()
        conn.close()

        if not orders:
            tk.Label(orders_list, text="Заказов нет", fg="gray", font=("Arial", 11)).pack(pady=50)
            return

        # Выводим каждый заказ
        for order_id, customer_name, phone, delivery_addr, status, courier_id in orders:
            status = str(status).strip()
            is_my_order = (courier_id == user_id)
            
            # Цвет фона: голубой для своих заказов, белый для свободных
            card_bg = "#F0F9FF" if is_my_order else "#FFFFFF"
            
            # Карточка заказа
            order_card = tk.Frame(orders_list, bd=1, relief="solid", pady=10, padx=10, bg=card_bg)
            order_card.pack(fill="x", pady=5)

            # Определяем кнопку и статус в зависимости от текущего статуса
            button_text = None
            next_status = None
            button_color = "#ddd"
            display_status = status
            button_enabled = True

            if status in ["0", "Оплачено", "None"]:
                button_text = "Принять ✓"
                next_status = "1"
                button_color = "#D1F2EB"
                display_status = "Новый"
                # Проверяем ограничение: один заказ на курьера
                if not is_my_order and has_active_order(user_id):
                    button_enabled = False
            elif status == "1":
                button_text = "Забрал 📦"
                next_status = "2"
                button_color = "#D6EAF8"
                display_status = "Принят"
            elif status == "2":
                button_text = "Доставлен ✅"
                next_status = "3"
                button_color = "#D4EFDF"
                display_status = "В пути"

            # Информация о заказе
            prefix = "МОЙ | " if is_my_order else "НОВЫЙ | "
            
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
                items_text += f"  • {item_title}: {item_amount} шт.\n"
            
            order_info = (f"{prefix}Заказ #{order_id}\n"
                         f"Клиент: {customer_name} | ☎️{phone}\n"
                         f"Адрес: {delivery_addr}\n\n"
                         f"Товары:\n{items_text.rstrip()}")
            
            tk.Label(order_card, text=order_info, justify="left", bg=card_bg, font=("Arial", 10)).pack(side="left")

            # Кнопка действия
            action_frame = tk.Frame(order_card, bg=card_bg)
            action_frame.pack(side="right")

            if button_text:
                btn = tk.Button(action_frame, text=button_text, bg=button_color, width=15, font=("Arial", 9, "bold"),command=lambda oid=order_id, ns=next_status: update_order_status(oid, ns),state="normal" if button_enabled else "disabled")
                btn.pack()
                
                tk.Label(action_frame, text=f"Статус: {display_status}", font=("Arial", 8), bg=card_bg).pack()

    # === ПАНЕЛЬ УПРАВЛЕНИЯ ВНИЗУ ===
    bottom_panel = tk.Frame(root, pady=10, bd=1, relief="raised")
    bottom_panel.pack(side="bottom", fill="x")

    tk.Button(bottom_panel, text="📊 Мой заработок", command=show_earnings, bg="#EBDEF0", width=15, font=("Arial", 9, "bold")).pack(side="left", padx=20)
    
    tk.Button(bottom_panel, text="🔄 Обновить", command=refresh_orders, width=12).pack(side="left")
    
    tk.Button(bottom_panel, text="🚪 Выйти", command=logout_callback, bg="#FADBD8", width=10).pack(side="right", padx=20)

    # Загружаем заказы сразу
    refresh_orders()