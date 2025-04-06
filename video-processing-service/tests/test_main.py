import json
from app import main

def test_callback_success(monkeypatch):
    # Variáveis para capturar o comportamento
    ack_called = False
    process_called = False

    # Criamos um fake channel para capturar chamadas
    class FakeChannel:
        def basic_ack(self, delivery_tag):
            nonlocal ack_called
            ack_called = True
        def basic_publish(self, exchange, routing_key, body, properties=None):
            # Se chegar aqui, não é esperado no fluxo de sucesso
            raise Exception("Não deveria publicar mensagem em fluxo de sucesso")

    fake_channel = FakeChannel()
    fake_method = type("FakeMethod", (), {"delivery_tag": "tag-123"})()
    fake_properties = None

    # Substitui a função process_video para controlar o fluxo
    def fake_process_video(filename, user_email):
        nonlocal process_called
        process_called = True

    monkeypatch.setattr(main, "process_video", fake_process_video)

    # Cria payload válido
    payload = {"filename": "video.mp4", "user_email": "test@example.com"}
    body = json.dumps(payload)

    # Chama o callback
    main.callback(fake_channel, fake_method, fake_properties, body)

    # Verifica se process_video e basic_ack foram chamados
    assert process_called is True
    assert ack_called is True

def test_callback_incomplete_payload(monkeypatch):
    calls = {}

    class FakeChannel:
        def basic_ack(self, delivery_tag):
            calls['ack'] = delivery_tag
        def basic_publish(self, exchange, routing_key, body, properties=None):
            calls['publish'] = (exchange, routing_key, body, properties)

    fake_channel = FakeChannel()
    fake_method = type("FakeMethod", (), {"delivery_tag": "tag-456"})()
    fake_properties = None

    # Mesmo que process_video seja chamado em fluxos válidos, aqui não deve ser chamado.
    monkeypatch.setattr(main, "process_video", lambda f, u: None)

    # Payload incompleto (falta user_email)
    payload = {"filename": "video.mp4"}
    body = json.dumps(payload)

    # Chama o callback que deve disparar o tratamento de exceção e publicar na DLQ
    main.callback(fake_channel, fake_method, fake_properties, body)

    # Verifica se basic_ack foi chamado e se a mensagem foi publicada para a DLQ
    assert calls.get('ack') == "tag-456"
    published = calls.get('publish')
    assert published is not None
    # O nome da DLQ está definido em main.DLQ_NAME
    assert published[1] == main.DLQ_NAME
