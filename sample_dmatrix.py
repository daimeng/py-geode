import aiohttp
import pandas as pd
import numpy as np
import sys
import os
import asyncio
import uvloop

from geode.dispatcher import AsyncDispatcher

async def main():
    client = await AsyncDispatcher.init()
    origins_file = sys.argv[1]
    destinations_file = sys.argv[2]

    origf = pd.read_csv(origins_file)[['lat', 'lon']].round(4).drop_duplicates()
    destf = pd.read_csv(destinations_file)[['lat', 'lon']].round(4).drop_duplicates()

    appendf = None
    append_file = None
    if len(sys.argv) >= 4:
        append_file = sys.argv[3]

        appendf = pd.read_csv(append_file)
        appendf = appendf[appendf.source == 'google'].drop_duplicates()
        appendf.set_index(pd.MultiIndex.from_arrays([appendf.olat, appendf.olon, appendf.dlat, appendf.dlon]), inplace=True)

    origs = origf.values
    dests = destf.values

    async with aiohttp.ClientSession() as session:
        res = await client.distance_matrix(
            origins=origs,
            destinations=dests,
            session=session,
            provider='google'
        )

    df = res.reset_index()
    if append_file:
        df.to_csv(append_file, mode='a', index=False, header=False, chunksize=1000)
    else:
        df.to_csv('test.csv', index=False, chunksize=1000)

if __name__ == '__main__':
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    asyncio.run(main())
