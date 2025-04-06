import os
from fastapi.testclient import TestClient
from app.main import app
from app.models import Video
from app.routes import get_db

client = TestClient(app)

# Classes para simular uma sessão de banco de dados fake
class FakeQuery:
    def __init__(self, videos):
        self._videos = videos

    def all(self):
        return self._videos

class FakeDBSession:
    def __init__(self, videos):
        self._videos = videos

    def query(self, model):
        return self

    def filter_by(self, **kwargs):
        user_email = kwargs.get("user_email")
        filtered = [video for video in self._videos if video.user_email == user_email]
        return FakeQuery(filtered)

    def close(self):
        pass

# Fake de get_db para injetar uma sessão fake
def fake_get_db():
    # Cria alguns objetos Video de teste
    video1 = Video(filename="video1.mp4", status="done", user_email="test@example.com")
    video2 = Video(filename="video2.mp4", status="processing", user_email="test@example.com")
    session = FakeDBSession([video1, video2])
    yield session

# Sobrescreve a dependência get_db do FastAPI
app.dependency_overrides[get_db] = fake_get_db

def test_list_videos():
    response = client.get("/videos?user_email=test@example.com")
    assert response.status_code == 200

    data = response.json()
    expected = [
        {
            "filename": "video1.mp4",
            "status": "done",
            "download_url": "/download/video1.zip"
        },
        {
            "filename": "video2.mp4",
            "status": "processing",
            "download_url": None
        }
    ]
    assert data == expected

def test_download_zip_file_exists(monkeypatch):
    # Simula que o arquivo existe
    def fake_exists(path):
        return True
    monkeypatch.setattr(os.path, "exists", fake_exists)

    # Cria um fake stat result para simular um arquivo existente
    fake_stat = os.stat_result((0o100644, 0, 0, 0, 0, 0, 1024, 0, 0, 0))
    monkeypatch.setattr(os, "stat", lambda path: fake_stat)

    # Monkeypatch anyio.open_file para retornar um objeto fake que imite um arquivo
    import anyio

    class DummyFile:
        async def read(self, n=-1):
            return b"dummy data"
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            pass

    async def fake_open_file(path, mode="rb"):
        return DummyFile()

    monkeypatch.setattr(anyio, "open_file", fake_open_file)

    response = client.get("/download/video1.zip")
    assert response.status_code == 200
    # Verifica se o Content-Type indica um arquivo zip
    assert response.headers["content-type"] == "application/zip"

def test_download_zip_file_not_exists(monkeypatch):
    # Simula que o arquivo não existe
    def fake_exists(path):
        return False

    monkeypatch.setattr(os.path, "exists", fake_exists)
    response = client.get("/download/video1.zip")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Arquivo não encontrado"
