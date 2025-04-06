import pika
import json
import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

def publish_to_queue(data):
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue="video_to_process", durable=True)

    channel.basic_publish(
        exchange='',
        routing_key='video_to_process',
        body=json.dumps(data)
    )
    connection.close()