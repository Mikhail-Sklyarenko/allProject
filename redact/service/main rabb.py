import pika
import json

def send_audit_message(action, details):
    """
    Отправка сообщений в очередь RabbitMQ.
    :param action: Действие (например, 'login', 'add_to_cart')
    :param details: Дополнительные сведения (например, ID пользователя, товар)
    """
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='audit_queue')

        message = {"action": action, "details": details}
        channel.basic_publish(exchange='', routing_key='audit_queue', body=json.dumps(message))
        print(f"Сообщение отправлено: {message}")
        connection.close()
    except Exception as e:
        print(f"Ошибка отправки сообщения: {e}")

# Пример использования
send_audit_message("login", {"user_id": 1, "username": "user_example"})
send_audit_message("add_to_cart", {"user_id": 1, "product_id": 101, "quantity": 2})
