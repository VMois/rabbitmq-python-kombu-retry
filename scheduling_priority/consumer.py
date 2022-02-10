from time import sleep
from kombu import Connection, Queue, Exchange
from kombu.mixins import ConsumerMixin

rabbit_url = "amqp://localhost:5672/"
MAX_RETRIES = 3
REQUEUE_DELAY= 15  # in seconds
conn = Connection(rabbit_url)
exchange = Exchange("", type="direct")
queue = Queue("workflow-submission", type="direct", routing_key="workflow-submission", exchange=exchange, max_priority=10)


class Worker(ConsumerMixin):
    def __init__(self, connection, queue):
        self.connection = connection
        self.queue = queue
        channel = self.connection.channel()
        queue(channel).declare()

        self.producer = self.connection.Producer()

        self.publish = self.connection.ensure(
            self.producer,
            self.producer.publish,
            max_retries=3,
        )


    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=self.queue,
                         callbacks=[self.on_message],
                         prefetch_count=1)]

    def on_message(self, body, message):
        retries_count = message.headers.get("x-retries", 0)
        print(f'got message: {body}, retries_count: {retries_count}')
        if "Fail" in body:
            if retries_count < MAX_RETRIES:
                sleep(REQUEUE_DELAY)
                message.reject()
                priority = message.properties["priority"]
                self.publish(body, 
                         headers={
                            "x-retries": retries_count + 1,
                         }, priority=priority, declare=[queue], exchange=exchange, routing_key="workflow-submission")
                print(f"retry {body}")
            else:
                message.reject()
                print(f"No more retries left for {body}. Rejected and update status to failed")
        else:
            sleep(REQUEUE_DELAY)
            message.ack()

if __name__ == "__main__":
    worker = Worker(conn, queue)
    worker.run()
