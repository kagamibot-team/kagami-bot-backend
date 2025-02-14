import asyncio
import json

import requests
from loguru import logger


def request_new_tst(url: str) -> bytes:
    content: bytes = requests.get(url).content

    if len(content) < 128 and content[0:1] == b"{":
        try:
            content_text = content.decode()
            json.loads(content_text)
            raise Exception(f"下载图片 {url} 时出错：{content_text}")
        except UnicodeDecodeError:
            pass
        except json.JSONDecodeError:
            pass

    return content


async def download(url: str) -> bytes:
    loop = asyncio.get_event_loop()

    logger.debug(f"开始从 URL 中下载资源：{url}")
    async with asyncio.timeout(120):
        data = await loop.run_in_executor(None, request_new_tst, url)
    logger.debug(f"资源下载完成：{url}")

    return data


__all__ = ["download"]
