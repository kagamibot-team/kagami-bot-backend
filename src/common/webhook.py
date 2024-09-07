import json
from typing import Any

import requests

from utils.threading import make_async


@make_async
def send_webhook(webhook_url: str, message: dict[str, Any] | str | list[Any]):
    """
    发送 Webhook 消息，使用 POST 形式
    """

    if isinstance(message, (dict, list)):
        message = json.dumps(message, ensure_ascii=False)
    elif isinstance(message, str):
        pass
    else:
        raise TypeError(f"message type {type(message)} is not supported")

    requests.post(
        webhook_url, data=message, headers={"Content-Type": "application/json"}
    )
