import os
import json
import threading
import pika
from fastapi import FastAPI

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

def start_consumer():
    print("[*] Aguardando mensagens do RabbitMQ...")
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

@app.on_event("startup")
def startup_event():
    thread = threading.Thread(target=start_consumer, daemon=True)
    thread.start()
