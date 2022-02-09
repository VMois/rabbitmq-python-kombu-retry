# RabbitMQ Python Kombu message retry

Based on [this article](https://engineering.nanit.com/rabbitmq-retries-the-full-story-ca4cc6c5b493).

1. Build RabbitMQ:

```bash
$ docker build -t rabbitmq-delay .
```

2. Start RabbitMQ:

```bash
$ docker run -d -p 5672:5672 -p 15672:15672 --hostname my-rabbit --name some-rabbit rabbitmq-delay
```

3. Install kombu:

```bash
$ pip3 install kombu
```

4. WIP