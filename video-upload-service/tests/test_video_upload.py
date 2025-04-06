import io
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
import json

# Importa o "app" de "app/main.py"
from app.main import app

client = TestClient(app)

def fake_session():
    class FakeSession:
        def add(self, obj):
            pass
        def commit(self):
            pass
        def close(self):
            pass
    return FakeSession()

def fake_blocking_connection(params):
    class FakeChannel:
        def queue_declare(self, queue, durable):
            pass
        def basic_publish(self, exchange, routing_key, body):
            assert routing_key == "video_to_process"
    class FakeConnection:
        def channel(self):
            return FakeChannel()
        def close(self):
            pass
    return FakeConnection()

def test_upload_video(monkeypatch):
    # Substitui a SessionLocal do routes.py
    monkeypatch.setattr("app.routes.SessionLocal", fake_session)
    # Substitui a conexão do pika
    monkeypatch.setattr("app.routes.pika.BlockingConnection", fake_blocking_connection)

    file_content = b"conteudo de video"
    files = {
        "file": ("video.mp4", io.BytesIO(file_content), "video/mp4")
    }

    response = client.post("/upload?user_email=test@example.com", files=files)
    assert response.status_code == 200

    data = response.json()
    assert "Upload realizado com sucesso" in data["message"]
    assert "filename" in data
