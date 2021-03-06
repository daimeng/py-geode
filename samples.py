import aiohttp
import time
import ujson
import asyncio
import prettyprinter
import numpy as np
import pandas as pd

from geode.dispatcher import AsyncDispatcher

prettyprinter.install_extras(include=['dataclasses'])

pd.set_option('display.float_format', '{:.4f}'.format)

async def main():
    client = await AsyncDispatcher.init()

    s = time.time()
    res = None

    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:

        # if len(sys.argv) > 1 and sys.argv[1] == 'g':
        #     res = await client.batch_geocode([
        #         '500 Rutherford Ave, Charlestown MA',
        #         'Cake Factory',
        #         '21 Henr St, Bristol, UK',
        #         'TD Bank 250 Cambridge Street Boston, MA 02114',
        #         m.GeoPoint(lon=-94.5823, lat=34.1368)
        #     ], session=session)
        # else:
        res = await client.distance_matrix(
            origins=np.array([
                (37.1165, -92.2353),
                (34.1368, -94.5823),
                (37.1165, -92.2353)
            ]),
            destinations=np.array([
                (34.1368, -94.5823),
                (36.3408, -96.0384),
                (32.2834, -92.0286),
                (32.2834, -92.0286)
            ]),
            session=session,
            provider='google')

    t = time.time() - s
    prettyprinter.pprint(res)
    print('Duration: %dms' % (t * 1000))


if __name__ == '__main__':
    asyncio.run(main())
