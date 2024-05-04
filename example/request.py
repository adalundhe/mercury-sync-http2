import asyncio

from mercury_sync_http2 import MercuryHTTP2Client


async def run():
    client = MercuryHTTP2Client()

    response = await client.get('https://http2.github.io/')
    print(response)


asyncio.run(run())