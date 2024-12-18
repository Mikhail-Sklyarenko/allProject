import pika
import sqlite3
import json

# Функция для инициализации базы данных
def init_audit_db():
    """
    Создает таблицу для хранения статистики, если она не существует.
    """
    conn = sqlite3.connect("audit_database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            details TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print("База данных аудита инициализирована.")

# Функция для сохранения статистики в базу данных
def save_to_db(action, details):
    """
    Сохраняет действие пользователя в базу данных.
    :param action: Тип действия (например, 'login', 'add_to_cart')
    :param details: Дополнительные сведения о действии
    """
    try:
        conn = sqlite3.connect("audit_database.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audit_logs (action, details) VALUES (?, ?)
        """, (action, json.dumps(details)))
        conn.commit()
        print(f"Действие '{action}' успешно сохранено в базу данных.")
    except Exception as e:
        print(f"Ошибка сохранения данных: {e}")
    finally:
        conn.close()

# Основная функция для получения сообщений из RabbitMQ
def consume_audit_logs():
    """
    Получает сообщения из очереди RabbitMQ и сохраняет их в базу данных.
    """
    def callback(ch, method, properties, body):
        """
        Обработка каждого сообщения из очереди.
        """
        print(f"Получено сообщение: {body}")
        try:
            # Декодирование сообщения
            message = json.loads(body)
            action = message.get("action")
            details = message.get("details")
            # Сохранение сообщения в базу данных
            save_to_db(action, details)
        except Exception as e:
            print(f"Ошибка обработки сообщения: {e}")

    try:
        # Подключение к RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='audit_queue')

        print("Ожидание сообщений... Для выхода нажмите CTRL+C")
        # Подписка на очередь
        channel.basic_consume(queue='audit_queue', on_message_callback=callback, auto_ack=True)

        # Запуск прослушивания очереди
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Микросервис остановлен.")
    except Exception as e:
        print(f"Ошибка подключения к RabbitMQ: {e}")

# Инициализация базы данных и запуск прослушивания
if __name__ == "__main__":
    init_audit_db()
    consume_audit_logs()
