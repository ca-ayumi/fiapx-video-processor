import os
import json
from app import processor

def test_process_video_file_not_found(monkeypatch):
    calls = {}

    def fake_publish_error_notification(user_email, filename, reason):
        calls['called'] = True
        calls['user_email'] = user_email
        calls['filename'] = filename
        calls['reason'] = reason

    monkeypatch.setattr(processor, "publish_error_notification", fake_publish_error_notification)

    def fake_exists(path):
        if path.startswith("/tmp/uploads"):
            return False  # Simula que o vídeo não foi encontrado
        return os.path.exists(path)
    monkeypatch.setattr(os.path, "exists", fake_exists)

    filename = "nonexistent_video.mp4"
    user_email = "test@example.com"
    processor.process_video(filename, user_email)

    assert calls.get('called') == True
    assert "não encontrado" in calls.get('reason')


def test_process_video_invalid_video(monkeypatch, tmp_path):
    """
    Testa o cenário em que o vídeo existe mas não pode ser aberto pelo OpenCV.
    """
    filename = "video.mp4"

    uploads_dir = tmp_path / "uploads"
    uploads_dir.mkdir()
    video_path = uploads_dir / filename
    video_path.write_text("dummy content")

    original_exists = os.path.exists

    def fake_exists(path):
        if path == f"/tmp/uploads/{filename}":
            return True
        return original_exists(path)

    monkeypatch.setattr(os.path, "exists", fake_exists)

    class FakeVideoCapture:
        def __init__(self, path):
            self.path = path

        def isOpened(self):
            return False

        def read(self):
            return (False, None)

        def release(self):
            pass

    import cv2
    monkeypatch.setattr(cv2, "VideoCapture", FakeVideoCapture)

    calls = {}

    def fake_notify_error(filename, user_email, reason):
        calls['notified'] = True
        calls['reason'] = reason

    monkeypatch.setattr(processor, "notify_error", fake_notify_error)

    processor.process_video(filename, "test@example.com")

    assert calls.get('notified') is True
    assert "Não foi possível abrir o vídeo" in calls.get('reason') or "Formato inválido" in calls.get('reason')