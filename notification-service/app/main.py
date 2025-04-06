import os
import json
import threading
import pika
from fastapi import FastAPI, Query
from .database import SessionLocal
from .models import Video
from .mailer import send_email_notification

app = FastAPI()

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
QUEUE_NAME = "video_status_updates"

def callback(ch, method, properties, body):
    print("[x] Mensagem recebida:", body)
    data = json.loads(body)

    db = SessionLocal()
    try:
        video = db.query(Video).filter_by(filename=data["filename"]).first()
        if video:
            video.status = data["status"]
            db.commit()

            # Envia e-mail
            send_email_notification(video.user_email, video.filename)
        else:
            print(f"[!] Vídeo {data['filename']} não encontrado no banco.")
    except Exception as e:
        print(f"[X] Erro ao processar mensagem: {e}")
    finally:
        db.close()

def handle_success_message(body):
    data = json.loads(body)
    filename = data.get("filename")
    to_email = data.get("user_email")
    if filename and to_email:
        send_email_notification(to_email, filename)

def handle_error_message(body):
    data = json.loads(body)
    filename = data.get("filename")
    to_email = data.get("user_email")
    error = data.get("error", "Erro desconhecido")

    if to_email and filename:
        send_email_notification(
            to_email,
            filename,
            error_message=error
        )

def start_consumer():
    print("[*] Notifier ouvindo filas de sucesso e erro...")
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    # Fila de sucesso
    channel.queue_declare(queue="video_status_updates", durable=True)
    channel.basic_consume(
        queue="video_status_updates",
        on_message_callback=lambda ch, method, properties, body: handle_success_message(body),
        auto_ack=True
    )

    # Fila de erro
    channel.queue_declare(queue="video_error_notifications", durable=True)
    channel.basic_consume(
        queue="video_error_notifications",
        on_message_callback=lambda ch, method, properties, body: handle_error_message(body),
        auto_ack=True
    )

    channel.start_consuming()

@app.on_event("startup")
def startup_event():
    threading.Thread(target=start_consumer, daemon=True).start()