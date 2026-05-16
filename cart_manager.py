import ui.ui_payment as ui_payment

def load_cart(user_id):
    # Загружаем корзину пользователя из файла
    user_id = str(user_id)
    cart_data = {}
    
    # Если файла еще нет, возвращаем пустую корзину
    try:
        file = open('cart.txt', 'r', encoding='utf-8')
    except FileNotFoundError:
        return cart_data
    
    # Читаем файл и парсим данные
    with file:
        for line in file:
            parts = line.strip().split(';')
            # Проверяем, что формат строки верный и это нужный пользователь
            if len(parts) == 5 and parts[0] == user_id:
                product_id = parts[1]
                cart_data[product_id] = {
                    'title': parts[2], 
                    'price': float(parts[3]), 
                    'amount': int(parts[4])
                }
    
    return cart_data

def save_cart(user_id, cart_data):
    # Сохраняем корзину пользователя
    user_id = str(user_id)
    new_lines = []
    
    # Читаем старый файл и сохраняем корзины других пользователей
    try:
        with open('cart.txt', 'r', encoding='utf-8') as file:
            for line in file:
                # Если это не строка текущего пользователя, сохраняем её
                if not line.startswith(user_id + ';'):
                    new_lines.append(line.strip())
    except FileNotFoundError:
        pass
    
    # Добавляем обновленные товары текущего пользователя
    for product_id, info in cart_data.items():
        line = f"{user_id};{product_id};{info['title']};{info['price']};{info['amount']}"
        new_lines.append(line)
    
    # Записываем все данные обратно в файл
    with open('cart.txt', 'w', encoding='utf-8') as file:
        for line in new_lines:
            file.write(line + '\n')