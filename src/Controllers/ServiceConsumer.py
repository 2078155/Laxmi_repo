import pika
from src.Controllers import TaskProcessing

_DELIVERY_MODE_PERSISTENT = 2

# Configuration
RABBITMQ_HOST = 'localhost'  #  os.environ.get("RABBIT_MQ_HOST")  'localhost'
RABBITMQ_PORT = 5672  #  os.environ.get("RABBIT_MQ_PORT")  5672
RABBITMQ_HEARTBEAT = 0  # int(os.environ.get("RABBIT_MQ_HEARTBEAT"))
RETRY_DELAY_MS = 30000

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, heartbeat=RABBITMQ_HEARTBEAT,
                              blocked_connection_timeout=60000)
)
channel = connection.channel()
channel.queue_declare(queue='rpcQueue', durable=True)

channel.basic_qos(prefetch_count=1)


def extract_keywords(ch, method, properties, body):
    task_processing = TaskProcessing.TaskProcessing()
    text = task_processing.process_task(body,properties.correlation_id)
    ch.basic_publish(exchange='',
                     routing_key=properties.reply_to,
                     properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                     body=str(text))
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_consume(extract_keywords, queue='rpcQueue')
channel.start_consuming()
