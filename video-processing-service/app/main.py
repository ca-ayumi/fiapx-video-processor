import os
import json
import threading
import pika
from .processor import process_video

DLQ_NAME = "video_to_process_dlq"
MAIN_QUEUE = "video_to_process"

def callback(ch, method, properties, body):
    print("[x] Mensagem recebida na fila:", body)
    try:
        payload = json.loads(body)
        filename = payload.get("filename")
        user_email = payload.get("user_email")

        if not filename or not user_email:
            raise ValueError(f"Payload incompleto: {payload}")

        print(f"[>] Processando vídeo: {filename} para usuário {user_email}")
        process_video(filename, user_email)

    except Exception as e:
        print(f"[!] Erro durante o processamento: {e}")
        ch.basic_publish(
            exchange="",
            routing_key=DLQ_NAME,
            body=body,
            properties=pika.BasicProperties(delivery_mode=2)  # persistente
        )
        print(f"[→] Mensagem movida para a DLQ: {DLQ_NAME}")
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)

def run():
    print("[*] Conectando ao RabbitMQ...")
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel()

    # Declara as filas
    channel.queue_declare(queue=MAIN_QUEUE, durable=True)
    channel.queue_declare(queue=DLQ_NAME, durable=True)

    channel.basic_qos(prefetch_count=1)  # processa uma por vez por worker
    channel.basic_consume(queue=MAIN_QUEUE, on_message_callback=callback)

    print("[*] Esperando mensagens...")
    channel.start_consuming()

if __name__ == "__main__":
    threading.Thread(target=run).start()