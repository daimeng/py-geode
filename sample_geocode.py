import aiohttp
import sys
import os
import time
import ujson
import asyncio
import uvloop
import prettyprinter
import numpy as np

import geode.models as m
from geode.dispatcher import AsyncDispatcher
from geode.config import yaml

prettyprinter.install_extras(include=['dataclasses'])

async def main():
    client = await AsyncDispatcher.init()

    s = time.time()
    res = None

    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:

        res = await client.geocode(
            '500 Rutherford Ave, Charlestown MA',
            session=session,
            provider='google'
        )

    t = time.time() - s
    prettyprinter.pprint(res)
    print('Duration: %dms' % (t * 1000))

if __name__ == '__main__':
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    asyncio.run(main())
