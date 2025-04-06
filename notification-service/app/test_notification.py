import pika
import json

# Conexão com RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()

# Declaração da fila
channel.queue_declare(queue="video_status_updates", durable=True)

# Dados de teste (simula o fim do processamento do vídeo)
message = {
    "filename": "exemplo_video_fiapx.mp4",
    "status": "done"
}

# Envio da mensagem
channel.basic_publish(
    exchange="",
    routing_key="video_status_updates",
    body=json.dumps(message),
    properties=pika.BasicProperties(delivery_mode=2)  # mensagem persistente
)

print("[x] Mensagem de status enviada com sucesso!")

connection.close()
