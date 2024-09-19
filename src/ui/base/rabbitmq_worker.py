import uuid

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

from src.ui.base.render_worker import RenderWorker


class RenderRpcClient:
    def __init__(
        self, host: str, port: int, virtual_host: str, username: str, password: str
    ):
        # 建立与 RabbitMQ 的连接
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=host,
                port=port,
                virtual_host=virtual_host,
                credentials=pika.PlainCredentials(
                    username=username,
                    password=password,
                ),
            )
        )
        self.channel = self.connection.channel()

        # 声明用于接收渲染结果的回调队列
        result = self.channel.queue_declare(queue="", exclusive=True)
        self.callback_queue = result.method.queue

        # 设置回调，当接收到 `render_result` 队列的消息时调用 on_response
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
        )

        # 初始化两个用于存储响应的属性
        self.response = None
        self.corr_id = None

    def on_response(
        self,
        ch: BlockingChannel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
    ):
        # 如果 correlation_id 匹配，存储响应
        if self.corr_id == properties.correlation_id:
            self.response = body
            ch.basic_ack(delivery_tag=method.delivery_tag or 0)

    def render(self, render_request: str):
        # 为每个请求生成一个唯一的 correlation_id
        self.corr_id = str(uuid.uuid4())
        self.response = None

        # 发送请求消息到 `render` 队列，附带 correlation_id 和回调队列
        self.channel.basic_publish(
            exchange="",
            routing_key="render",
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,  # 回调队列，用于接收渲染结果
                correlation_id=self.corr_id,  # 唯一的 correlation_id，用于匹配请求和响应
            ),
            body=render_request.encode(),
        )

        # 等待响应，当响应为 None 时，继续轮询
        while self.response is None:
            self.connection.process_data_events()  # 非阻塞等待

        return self.response


class RabbitMQWorker(RenderWorker):
    _client: RenderRpcClient | None

    def __init__(
        self, host: str, port: int, virtual_host: str, username: str, password: str
    ) -> None:
        super().__init__()
        self.host = host
        self.port = port
        self.virtual_host = virtual_host
        self.username = username
        self.password = password

    def _init(self):
        self._client = RenderRpcClient(
            self.host, self.port, self.virtual_host, self.username, self.password
        )

    @property
    def client(self):
        assert self._client is not None, "RabbitMQ 客户端未启动！"
        return self._client

    def _render(self, link: str) -> bytes:
        return self.client.render(link)

    def _ok(self) -> bool:
        return self.client.connection.is_open

    def _quit(self):
        if self._client:
            self._client.connection.close()
            self._client = None
