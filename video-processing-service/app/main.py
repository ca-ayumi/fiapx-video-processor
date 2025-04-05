import os
import json
import threading
import pika
from .processor import process_video

def callback(ch, method, properties, body):
    print("[x] Mensagem recebida na fila:", body)
    payload = json.loads(body)
    filename = payload.get("filename")
    user_email = payload.get("user_email")

    if not filename or not user_email:
        print("[!] Erro: Payload incompleto:", payload)
        return

    print(f"[>] Processando vídeo: {filename} para usuário {user_email}")
    process_video(filename, user_email)

def run():
    print("[*] Conectando ao RabbitMQ...")
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel()
    channel.queue_declare(queue="video_to_process")
    channel.basic_consume(queue="video_to_process", on_message_callback=callback, auto_ack=True)

    print("[*] Esperando mensagens...")
    channel.start_consuming()

if __name__ == "__main__":
    threading.Thread(target=run).start()
