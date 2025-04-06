import os
import cv2
import zipfile
from datetime import datetime
from .models import Video
from .database import SessionLocal
import pika
import json

def process_video(filename: str, user_email: str):
    print(f"\n[PROCESSAMENTO] Iniciando para: {filename}, usuário: {user_email}")

    input_path = os.path.join("/tmp/uploads", filename)
    frames_dir = os.path.join("/tmp/frames", filename.replace(".mp4", ""))
    zip_path = os.path.join("/tmp/processed", filename.replace(".mp4", "") + ".zip")

    if not os.path.exists(input_path):
        print(f"[ERRO] Arquivo de vídeo não encontrado em: {input_path}")
        return

    print(f"[OK] Vídeo encontrado: {input_path}")
    os.makedirs(frames_dir, exist_ok=True)
    print(f"[OK] Diretório de frames criado: {frames_dir}")

    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"[ERRO] Não foi possível abrir o vídeo com OpenCV: {input_path}")
        return

    print("[OK] Vídeo aberto com sucesso.")
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"[INFO] Fim do vídeo ou falha de leitura após {frame_count} frames.")
            break

        frame_path = os.path.join(frames_dir, f"frame_{frame_count}.jpg")
        success = cv2.imwrite(frame_path, frame)
        if success:
            print(f"[FRAME] Salvo: {frame_path}")
        else:
            print(f"[ERRO] Falha ao salvar frame: {frame_path}")

        frame_count += 1

    cap.release()
    print(f"[OK] Total de frames extraídos: {frame_count}")

    try:
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for root, _, files in os.walk(frames_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, frames_dir)
                    zipf.write(full_path, arcname)
        print(f"[ZIP OK] Arquivo gerado: {zip_path}")
    except Exception as e:
        print(f"[ERRO] Ao criar zip: {e}")
        return

    if not os.path.exists(zip_path):
        print(f"[ERRO] ZIP não criado em: {zip_path}")
        return

    db = SessionLocal()
    try:
        video = db.query(Video).filter_by(filename=filename, user_email=user_email).first()
        if video:
            video.status = "done"
            db.commit()
            print(f"[DB OK] Status atualizado para 'done' para vídeo: {filename}")
            publish_status_update(filename, "done", user_email)
        else:
            print(f"[DB ERRO] Vídeo não encontrado com filename={filename} e user_email={user_email}")
    except Exception as e:
        print(f"[DB EXCEPTION] {e}")
    finally:
        db.close()

def publish_status_update(filename, status, user_email):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
        channel = connection.channel()
        channel.queue_declare(queue="video_status_updates", durable=True)

        message = {
            "filename": filename,
            "status": status,
            "user_email": user_email
        }

        channel.basic_publish(
            exchange="",
            routing_key="video_status_updates",
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print(f"[RABBITMQ ✓] Mensagem enviada: {message}")
        connection.close()
    except Exception as e:
        print(f"[RABBITMQ ✗] Falha ao enviar mensagem: {e}")