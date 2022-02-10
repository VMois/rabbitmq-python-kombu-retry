from time import sleep
from consumer import exchange, queue
from kombu import Connection, Producer

rabbit_url = "amqp://localhost:5672/"

connection = Connection(rabbit_url)

channel = connection.channel()

producer = connection.Producer()

def error_callback(exception: Exception, interval: int):
    print(f"Error: {exception}")

publisher = connection.ensure(
    producer,
    producer.publish,
    errback=error_callback,
    max_retries=3,
)

def publish(body: str, priority: int):
    publisher(body, declare=[queue], exchange=exchange, routing_key="workflow-submission", priority=priority)


publish("Workflow 1 (OK)", 1)
sleep(1)
publish("Workflow 2 (OK)", 1)
sleep(1)
publish("Workflow 3 (OK)", 3)
sleep(1)
publish("Workflow 4 (OK)", 3)
sleep(1)
publish("Workflow 5 (Fail)", 4)
sleep(1)
publish("Workflow 6 (OK)", 2)

connection.release()
