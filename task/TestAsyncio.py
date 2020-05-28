import time
import asyncio

# 定义异步函数
async def add(x,y):
    await asyncio.sleep(1)
    print('Hello World:%s' % time.time())
    return x+y
if __name__ =='__main__':
    loop = asyncio.get_event_loop()
    task1=asyncio.ensure_future(add(1,2))
    task2=asyncio.ensure_future(add(2,3))
    dones,pending = asyncio.wait([task1, task2])
    loop.run_until_complete([task1, task2])
    print(dones.result())
    loop.close()
