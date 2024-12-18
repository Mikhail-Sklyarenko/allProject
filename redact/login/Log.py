import hashlib  # Для хеширования пароля (если он хешируется в базе)
import sqlite3  # База данных (пример на SQLite для наглядности)

def login_user(login, password):
    """
    Функция для авторизации пользователя.
    :param login: Логин пользователя
    :param password: Пароль пользователя
    :return: Сообщение о статусе авторизации
    """
    try:
        # Подключение к базе данных
        conn = sqlite3.connect("store_database.db")
        cursor = conn.cursor()

        # Хеширование пароля для сравнения с сохраненным (если хранится хеш)
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # SQL-запрос для поиска пользователя по логину и паролю
        cursor.execute("SELECT customers_id, number_of_logons FROM customers WHERE login = ? AND password = ?",
                       (login, hashed_password))
        user = cursor.fetchone()

        if user:
            # Если пользователь найден
            user_id, logins = user

            # Обновление данных пользователя: дата последнего входа и количество входов
            cursor.execute("""
                UPDATE customers 
                SET date_of_last_logon = CURRENT_TIMESTAMP, number_of_logons = ? 
                WHERE customers_id = ?
            """, (logins + 1, user_id))
            conn.commit()

            print("Авторизация успешна. Добро пожаловать!")
        else:
            print("Неверный логин или пароль.")

    except Exception as e:
        print(f"Ошибка на сервере: {e}")
    finally:
        # Закрытие соединения с базой данных
        conn.close()

# Пример вызова функции
login_user("user_example", "password123")
