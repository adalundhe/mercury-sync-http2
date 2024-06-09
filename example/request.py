import asyncio
import time

from mercury_sync_http2 import MercuryHTTP2Client


async def cancel(task: asyncio.Task):
    try:
        task.cancel()
        await task

    except Exception:
        pass


async def generate(time_limit: int=60):
    
    start = time.monotonic()
    elapsed = 0
    idx = 0

    while elapsed < time_limit:
        yield idx

        idx += 1

        await asyncio.sleep(0)
        
        elapsed = time.monotonic() - start


async def run(timeout: int=60):
    client = MercuryHTTP2Client(pool_size=500)


    start = time.monotonic()
    completed, pending = await asyncio.wait([
        asyncio.create_task(
            client.get('https://http2.github.io/')
        ) async for _ in  generate(time_limit=timeout)   
    ], timeout=timeout)

    elapsed = time.monotonic() - start

    results = await asyncio.gather(*[
        complete for complete in completed
    ])

    print('Completed: ', len(results)/elapsed)
    print(results[0].status)

    await asyncio.gather(*[
        cancel(pend) for pend in pending
    ])
    
async def run_single():

    client = MercuryHTTP2Client(pool_size=50)
    response = await client.get('https://http2.github.io/')
    print(response)



asyncio.run(run())