def add_category(name):
    """
    Добавление новой категории товаров.
    """
    conn = sqlite3.connect("store_database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO categories (categories_name, date_added) VALUES (?, CURRENT_TIMESTAMP)", (name,))
    conn.commit()
    conn.close()
    print("Категория добавлена.")
