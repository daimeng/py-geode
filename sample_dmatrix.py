import aiohttp
import pandas as pd
import numpy as np
import sys
import os
import time
import ujson
import asyncio
import uvloop
from scipy.spatial import distance

import geode.models as m
from geode import distances
from geode import google

MAX_METERS = 321869

async def main():
    client = google.Client(
        key=os.getenv('IA_GLOBAL_GOOGLE_API_KEY')
    )
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

    res = None

    origs = origf.to_records(index=False)
    dests = destf.to_records(index=False)

    hdists = distance.cdist(
        origs,
        dests,
        distances.gc_manhattan)

    # h0i = np.argsort(hdists, axis=0)
    # h0 = np.take_along_axis(hdists, h0i, axis=0)

    # h1i = np.argsort(h0, axis=1)
    # h1 = np.take_along_axis(h0, h1i, axis=1)

    # valid = h1 < MAX_METERS
    # v0 = valid.sum(0) > 0
    # v1 = valid.sum(1) > 0

    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        res = await asyncio.gather(*[
            client.distance_matrix(
                origins=orig,
                destinations=[
                    d
                    for d in dests[hdists[i] < MAX_METERS]
                    if appendf is None or (orig[0], orig[1], d[0], d[1]) not in appendf.index],
                session=session
            ) for i, orig in enumerate(origs)
        ])

    results = np.empty((len(origs), len(dests)), dtype=np.object)

    for i, orig in enumerate(origs):
        results[i] = [('%.4f' % orig[0], '%.4f' % orig[1], '%.4f' % dests[x][0], '%.4f' % dests[x][1], '%.0f' % d, 'gc_manhattan') for x, d in enumerate(hdists[i])]

        if not res[i]:
            continue

        r = iter(res[i].distances)

        for x, valid in enumerate(hdists[i] < MAX_METERS):
            if valid:
                entry = next(r, None)
                if entry:
                    results[i][x] = ('%.4f' % orig[0], '%.4f' % orig[1], '%.4f' % dests[x][0], '%.4f' % dests[x][1], '%.0f' % entry.meters, 'google')

    df = pd.DataFrame(results.flatten().tolist(), columns=['olat', 'olon', 'dlat', 'dlon', 'dist', 'source'])
    df = df[df.source == 'google']

    if append_file:
        df.to_csv(append_file, mode='a', index=False, header=False, chunksize=1000)
    else:
        df.to_csv('test.csv', index=False, chunksize=1000)

if __name__ == '__main__':
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    asyncio.run(main())
