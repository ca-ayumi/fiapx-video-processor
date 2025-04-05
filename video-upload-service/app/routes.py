from fastapi import APIRouter, UploadFile, File, Query, HTTPException
import shutil, os
import pika
import json
import uuid
from .database import SessionLocal
from .models import Video

router = APIRouter()

@router.post("/upload")
async def upload_video(file: UploadFile = File(...), user_email: str = Query(...)):
    db = SessionLocal()

    # Gera nome único
    filename = f"{uuid.uuid4()}_{file.filename}"
    save_path = f"/tmp/uploads/{filename}"
    os.makedirs("/tmp/uploads", exist_ok=True)

    # Salva arquivo
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Persiste no banco
    video = Video(filename=filename, user_email=user_email, status="processing")
    db.add(video)
    db.commit()
    db.close()

    # Envia para RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel()
    channel.queue_declare(queue="video_to_process")

    payload = {
        "filename": filename,
        "user_email": user_email
    }
    channel.basic_publish(
        exchange='',
        routing_key='video_to_process',
        body=json.dumps(payload)
    )
    connection.close()

    return {"message": "Upload realizado com sucesso", "filename": filename}
