import asyncio
import os
import time
from nonebot import get_bot
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from pydantic import BaseModel
from ..putils.pydanticData import PydanticDataManagerGlobal

import threading


class WumGlobal(BaseModel):
    lastCaught: float = 0


wumData = PydanticDataManagerGlobal(WumGlobal, os.path.join(os.getcwd(), 'data', 'wum', 'wum.json'))


async def catchWum():
    bot = get_bot('3687050325')

    await bot.call_api('send_group_msg', group_id = '600984291', message=Message([
            MessageSegment.text('抓wum')
        ]))


class IntervalThread(threading.Thread):
    def run(self) -> None:
        while True:
            with wumData as d:
                lc = d.lastCaught
            
            if time.time() - lc > 3600 * 4 + 15:
                time.sleep(3)
                try:
                    asyncio.run(catchWum())
                except:
                    pass
                
                with wumData as d:
                    d.lastCaught = time.time()
            
            time.sleep(100)


thread = IntervalThread()
thread.start()
