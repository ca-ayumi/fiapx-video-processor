import pika
import json
import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
QUEUE_NAME = "video_notifications"

def publish_error_notification(user_email: str, filename: str, reason: str):
    message = {
        "user_email": user_email,
        "filename": filename,
        "error": reason
    }

    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        channel.basic_publish(
            exchange="",
            routing_key=QUEUE_NAME,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print(f"[→] Notificação de erro publicada para {user_email}: {reason}")
        connection.close()
    except Exception as e:
        print(f"[X] Falha ao publicar notificação de erro: {e}")
