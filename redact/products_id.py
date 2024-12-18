def decrease_product_quantity(product_id, quantity_purchased):
    """
    Уменьшает количество товаров на складе после покупки.
    :param product_id: ID товара
    :param quantity_purchased: Количество покупаемого товара
    """
    try:
        conn = sqlite3.connect("store_database.db")
        cursor = conn.cursor()

        # Проверка текущего количества товара
        cursor.execute("SELECT quantity FROM products WHERE products_id = ?", (product_id,))
        result = cursor.fetchone()

        if result and result[0] >= quantity_purchased:
            # Уменьшение количества
            new_quantity = result[0] - quantity_purchased
            cursor.execute("UPDATE products SET quantity = ? WHERE products_id = ?", (new_quantity, product_id))
            conn.commit()
            print("Количество товаров обновлено.")
        else:
            print("Недостаточно товара на складе.")

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        conn.close()

# Пример вызова
decrease_product_quantity(1, 3)
