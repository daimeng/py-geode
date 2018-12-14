import aiohttp
import sys
import os
import time
import asyncio
import uvloop
import prettyprinter
import numpy as np

from geode import METERS_PER_MILE
from geode.dispatcher import AsyncDispatcher

prettyprinter.install_extras(include=['dataclasses'])

async def main():
    client = await AsyncDispatcher.init()

    s = time.time()

    async with aiohttp.ClientSession() as session:
        res = await client.distance_pairs(
            origins=np.array([
                (37.1165, -92.2353),
                (34.1368, -94.5823),
                (37.1165, -92.2353),
                (40.3283, -88.3080)
            ]),
            destinations=np.array([
                (34.1368, -94.5823),
                (36.3408, -96.0384),
                (32.2834, -92.0286),
                (40.3468, -88.2936)
            ]),
            max_meters=200 * METERS_PER_MILE,
            session=session,
            provider='google')

    t = time.time() - s
    prettyprinter.pprint(res)
    print('Duration: %dms' % (t * 1000))

if __name__ == '__main__':
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    asyncio.run(main())
