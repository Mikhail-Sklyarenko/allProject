def add_product(name, price, quantity, category_id):
    """
    Добавление нового товара в базу данных.
    """
    conn = sqlite3.connect("store_database.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (name, price, quantity, categories_id, date_added) 
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (name, price, quantity, category_id))
    conn.commit()
    conn.close()
    print("Товар добавлен.")
