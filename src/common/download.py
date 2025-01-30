import json
from pathlib import Path
import requests
import asyncio
import ssl


# IDK why but works
class TLSAdapter(requests.adapters.HTTPAdapter):  # type: ignore
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.set_ciphers("DEFAULT")
        kwargs["ssl_context"] = context
        return super().init_poolmanager(*args, **kwargs)  # type: ignore


def request_new_tst(url: str) -> bytes:
    session = requests.Session()
    session.mount("https://", TLSAdapter())
    response = session.get(url, verify=False)
    content: bytes = response.content
    
    if len(content) < 128 and content[0:1] == b'{':
        try:
            content_text = content.decode()
            json.loads(content_text)
            raise Exception(f"下载图片 {url} 时出错：{content_text}")
        except UnicodeDecodeError:
            pass
        except json.JSONDecodeError:
            pass
    
    return content


async def download(url: str):
    loop = asyncio.get_event_loop()

    return await loop.run_in_executor(None, request_new_tst, url)


__all__ = ["download"]
