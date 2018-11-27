import aiohttp
import sys
import os
import time
import ujson
import asyncio
import uvloop
import prettyprinter # type: ignore
import numpy as np # type: ignore

import geode.models as m
from geode import google

prettyprinter.install_extras(include=['dataclasses'])

async def main():
    client = google.Client(
        key=os.getenv('IA_GLOBAL_GOOGLE_API_KEY')
    )

    s = time.time()
    res = None

    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:

        if len(sys.argv) > 1 and sys.argv[1] == 'g':
            res = await client.batch_geocode([
                '500 Rutherford Ave, Charlestown MA',
                'Cake Factory',
                '21 Henr St, Bristol, UK',
                'TD Bank 250 Cambridge Street Boston, MA 02114',
                m.GeoPoint(lon=-94.5823, lat=34.1368)
            ], session=session)
        else:
            res = await client.distance_matrix(
                origins=np.array([
                    (37.1165, -92.2353),
                    (34.1368, -94.5823),
                    (37.1165, -92.2353)
                ]),
                destinations=np.array([
                    (-94.5823, 34.1368),
                    (-96.0384, 36.3408),
                    (-92.0286, 32.2834),
                    (-92.0286, 32.2834)
                ], dtype=[('lon', float), ('lat', float)]),
                session=session)

    t = time.time() - s
    prettyprinter.pprint(res)
    print('Duration: %dms' % (t * 1000))

if __name__ == '__main__':
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    asyncio.run(main())
