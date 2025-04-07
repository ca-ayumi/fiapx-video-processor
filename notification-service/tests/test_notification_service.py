import os
import json
import smtplib
from email.message import EmailMessage
import pytest

from app.mailer import send_email_notification, SMTP_HOST, SMTP_PORT
from app.main import handle_success_message, handle_error_message, callback
from app.models import Video


def test_send_email_notification_success(monkeypatch, capsys):
    class FakeSMTP:
        def __init__(self, host, port):
            self.host = host
            self.port = port
            self.started_tls = False
            self.logged_in = False
            self.sent_message = None

        def starttls(self):
            self.started_tls = True

        def login(self, username, password):
            self.logged_in = True
            self.username = username
            self.password = password

        def send_message(self, msg):
            self.sent_message = msg

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    monkeypatch.setattr(smtplib, "SMTP", lambda host, port: FakeSMTP(host, port))

    os.environ["SMTP_USERNAME"] = "test@example.com"

    send_email_notification("recipient@example.com", "video.mp4")

    captured = capsys.readouterr().out
    assert "[→] Tentando enviar e-mail para recipient@example.com sobre 'video.mp4'" in captured
    assert "[✓] E-mail enviado para recipient@example.com" in captured


def test_send_email_notification_error(monkeypatch, capsys):
    class FakeSMTP:
        def __init__(self, host, port):
            pass

        def starttls(self):
            pass

        def login(self, username, password):
            raise Exception("Login failed")

        def send_message(self, msg):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    monkeypatch.setattr(smtplib, "SMTP", lambda host, port: FakeSMTP(host, port))
    os.environ["SMTP_USERNAME"] = "test@example.com"

    send_email_notification("recipient@example.com", "video.mp4", error_message="Some error")
    captured = capsys.readouterr().out
    assert "[X] Erro ao enviar e-mail para recipient@example.com:" in captured

def test_handle_success_message(monkeypatch):
    calls = {}

    def fake_send_email_notification(to_email, filename, error_message=None):
        calls["to_email"] = to_email
        calls["filename"] = filename
        calls["error_message"] = error_message

    monkeypatch.setattr("app.main.send_email_notification", fake_send_email_notification)

    message = {"filename": "video.mp4", "user_email": "user@example.com"}
    handle_success_message(json.dumps(message))

    assert calls.get("to_email") == "user@example.com"
    assert calls.get("filename") == "video.mp4"
    assert calls.get("error_message") is None


def test_handle_error_message(monkeypatch):
    calls = {}

    def fake_send_email_notification(to_email, filename, error_message=None):
        calls["to_email"] = to_email
        calls["filename"] = filename
        calls["error_message"] = error_message

    monkeypatch.setattr("app.main.send_email_notification", fake_send_email_notification)

    message = {
        "filename": "video.mp4",
        "user_email": "user@example.com",
        "error": "Processing error"
    }
    handle_error_message(json.dumps(message))

    assert calls.get("to_email") == "user@example.com"
    assert calls.get("filename") == "video.mp4"
    assert calls.get("error_message") == "Processing error"

def test_callback_video_found(monkeypatch):
    class FakeVideo:
        def __init__(self, filename, status, user_email):
            self.filename = filename
            self.status = status
            self.user_email = user_email

    fake_video = FakeVideo("video.mp4", "processing", "user@example.com")

    class FakeQuery:
        def __init__(self, videos):
            self.videos = videos

        def first(self):
            return self.videos[0] if self.videos else None

    class FakeDBSession:
        def __init__(self, videos):
            self._videos = videos

        def query(self, model):
            return self

        def filter_by(self, **kwargs):
            # Filtra pelo filename
            if kwargs.get("filename") == fake_video.filename:
                return FakeQuery([fake_video])
            return FakeQuery([])

        def commit(self):
            pass

        def close(self):
            pass

    fake_db = FakeDBSession([fake_video])
    monkeypatch.setattr("app.main.SessionLocal", lambda: fake_db)

    calls = {}

    def fake_send_email_notification(to_email, filename, error_message=None):
        calls["to_email"] = to_email
        calls["filename"] = filename
        calls["error_message"] = error_message

    monkeypatch.setattr("app.main.send_email_notification", fake_send_email_notification)

    fake_channel = type("FakeChannel", (), {"basic_ack": lambda self, delivery_tag: None})()
    fake_method = type("FakeMethod", (), {"delivery_tag": "tag123"})()
    fake_properties = None

    message = {"filename": "video.mp4", "status": "done"}
    body = json.dumps(message)

    callback(fake_channel, fake_method, fake_properties, body)

    assert calls.get("to_email") == "user@example.com"
    assert calls.get("filename") == "video.mp4"
    assert calls.get("error_message") is None
