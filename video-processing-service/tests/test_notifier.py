import json
from app import notifier

def test_publish_error_notification_success(monkeypatch):
    calls = {}

    class FakeChannel:
        def queue_declare(self, queue, durable):
            calls['queue_declare'] = (queue, durable)
        def basic_publish(self, exchange, routing_key, body, properties):
            calls['basic_publish'] = (exchange, routing_key, body, properties)

    class FakeConnection:
        def channel(self):
            return FakeChannel()
        def close(self):
            pass

    def fake_blocking_connection(params):
        return FakeConnection()

    # Substitui o BlockingConnection do pika dentro do módulo notifier
    monkeypatch.setattr(notifier.pika, "BlockingConnection", fake_blocking_connection)

    user_email = "test@example.com"
    filename = "video.mp4"
    reason = "Erro de teste"

    notifier.publish_error_notification(user_email, filename, reason)

    # Verifica se a fila foi declarada corretamente
    assert calls.get('queue_declare') == ("video_notifications", True)

    # Verifica se a mensagem foi publicada corretamente
    expected_body = json.dumps({
        "user_email": user_email,
        "filename": filename,
        "error": reason
    })
    published = calls.get('basic_publish')
    assert published is not None
    assert published[1] == "video_notifications"
    assert published[2] == expected_body
