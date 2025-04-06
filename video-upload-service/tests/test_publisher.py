import json
from app.publisher import publish_to_queue

def test_publish_to_queue(monkeypatch):
    # Dicionário para registrar as chamadas realizadas
    calls = {}

    class FakeChannel:
        def queue_declare(self, queue, durable):
            calls['queue_declare'] = (queue, durable)

        def basic_publish(self, exchange, routing_key, body):
            calls['basic_publish'] = (exchange, routing_key, body)

    class FakeConnection:
        def channel(self):
            return FakeChannel()

        def close(self):
            pass

    def fake_blocking_connection(params):
        # Aqui você pode verificar os parâmetros se necessário
        return FakeConnection()

    # Substitui a função do pika no módulo publisher para evitar conexão real com o RabbitMQ
    monkeypatch.setattr("app.publisher.pika.BlockingConnection", fake_blocking_connection)

    # Dados de teste para publicar
    data = {"filename": "video.mp4", "user_email": "test@example.com"}

    # Chama a função que está sendo testada
    publish_to_queue(data)

    # Verifica se a fila foi declarada corretamente
    assert calls.get('queue_declare') == ("video_to_process", True), "Fila não foi declarada corretamente"

    # Verifica se a mensagem foi publicada com os parâmetros corretos
    expected_body = json.dumps(data)
    assert calls.get('basic_publish') == ("", "video_to_process", expected_body), "Parâmetros da publicação não batem"
