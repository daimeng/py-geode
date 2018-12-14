import aiohttp
import asyncio
import asyncpg
import os
import numpy as np
import pandas as pd
import ujson
import uvloop
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from threading import Thread
from scipy import spatial

from geode import google, dist_metrics
from geode.config import yaml
from geode.cache import PostgresCache
from geode.utils import create_dist_index, grouper, KEY_COLS

TYPE_MAP = {
    'google': google,
    # 'alk': alk,
    # 'bing': bing
}


MAX_METERS = 321869

class AsyncDispatcher:
    cache = None
    cache_conn = None
    providers = {}

    def __init__(self, config=None):
        # load default configs from home path config
        if not config:
            home = os.path.expanduser('~')
            user_config_path = os.path.join(home, '.geode', 'config.yml')
            # local_config_path = os.path.join('geode-config.yml')

            if os.path.exists(user_config_path) and os.path.isfile(user_config_path):
                config = yaml.load(open(user_config_path))

        # initialize providers
        if config.get('providers'):
            for k, opts in config['providers'].items():
                self.providers[k] = TYPE_MAP[opts['type_']].Client(**opts)

        # intialize cache
        if 'caching' in config:
            self.cache = PostgresCache(**config['caching'])

    @classmethod
    async def init(cls, config=None):
        instance = cls(config)
        if instance.cache:
            instance.cache_conn = await instance.cache.connection()
        return instance

    async def distance_matrix(self, origins, destinations, max_meters=MAX_METERS, session=None, provider=None):
        client = self.providers.get(provider)

        # prepare parameters and indices
        origins = np.unique(origins.round(4), axis=0)
        destinations = np.unique(destinations.round(4), axis=0)

        idx = create_dist_index(origins, destinations)

        # kick off cache request
        cache_future = asyncio.ensure_future(
            self.cache.get_distances(
                origins, destinations, provider=provider))

        estimates = spatial.distance.cdist(
            origins,
            destinations,
            dist_metrics.gc_manhattan)

        estimate_df = pd.DataFrame(estimates.ravel(), columns=['meters'], index=idx.index)
        estimate_df['seconds'] = estimate_df.meters / 30
        estimate_df['source'] = 'gc_manhattan'

        out_of_range = estimate_df.index[estimate_df.meters > max_meters]

        # wait on cache request
        cache_df = await cache_future
        cache_df['source'] = 'google'

        missing = pd.DataFrame(
            index=idx.index.difference(out_of_range).difference(cache_df.index))

        res = await asyncio.gather(*[
            client.distance_matrix(
                origins=[o],
                destinations=ds.loc[o].index.values,
                session=session
            ) for o, ds in missing.groupby(level=[0,1])
        ])

        res_df = None
        res_flat = [row.distances.ravel() for row in res if len(row.distances)]
        if res_flat:
            res_df = pd.DataFrame.from_records(
                np.concatenate(res_flat),
                index=missing.index)
            res_df['source'] = 'google'

        merged_df = pd.concat([estimate_df, cache_df, res_df], sort=False)

        merged_df = merged_df[~merged_df.index.duplicated(keep='last')].sort_index()

        await self.cache.set_distances(
            origins, destinations, res_df, provider=provider)

        return merged_df

    async def distance_pairs_shim(self, origins, destinations, session=None, provider=None):
        client = self.providers.get(provider)

        res = await asyncio.gather(*[
            client.distance_matrix(
                origins=o,
                destinations=d,
                session=session
            ) for o, d in zip(grouper(origins, 1), grouper(destinations, 1))
        ])

        return res

    async def distance_pairs(self, origins, destinations, max_meters=MAX_METERS, session=None, provider=None):
        client = self.providers.get(provider)

        origins = origins.round(4)
        destinations = destinations.round(4)

        idx = pd.DataFrame(np.hstack((origins, destinations)), columns=KEY_COLS).set_index(KEY_COLS)

        cache_future = asyncio.ensure_future(
            self.cache.get_distances(
                origins, destinations, provider=provider, pair=True))

        estimates = spatial.distance.cdist(
            origins,
            destinations,
            dist_metrics.gc_manhattan)

        estimate_df = pd.DataFrame(estimates.diagonal().ravel(), columns=['meters'], index=idx.index)
        estimate_df['seconds'] = estimate_df.meters / 30
        estimate_df['source'] = 'gc_manhattan'

        out_of_range = estimate_df.index[estimate_df.meters > MAX_METERS]

        cache_df = await cache_future
        cache_df['source'] = 'google'

        missing = pd.DataFrame(
            index=idx.index.difference(out_of_range).difference(cache_df.index))

        if hasattr(client, 'distance_pairs'):
            distance_pairs = client.distance_pairs
        else:
            distance_pairs = self.distance_pairs_shim
        
        # unpack
        res_df = None
        if not missing.index.empty:
            origins, destinations = zip(*[((a,b),(c,d))for a,b,c,d in missing.index])
            res = await distance_pairs(origins, destinations, session=session, provider=provider)
            res_df = pd.DataFrame.from_records(np.array([r.distances for r in res]).diagonal().flat, index=missing.index)
            res_df['source'] = 'google'

        merged_df = pd.concat([estimate_df, cache_df, res_df], sort=False)

        merged_df = merged_df[~merged_df.index.duplicated(keep='last')].sort_index()

        await self.cache.set_distances(
            origins, destinations, res_df, provider=provider)

        return merged_df


class Dispatcher:
    cache = None
    cache_conn = None
    providers = {}
    dispatcher = None
    loop = None

    def __init__(self, config=None):
        self.dispatcher = self.run(AsyncDispatcher.init(config))

    def run(self, coro):
        self.loop = self.loop or asyncio.new_event_loop()

        future = ThreadPoolExecutor().submit(self.loop.run_until_complete, coro)

        return future.result()

    async def distance_matrix_with_session(self, origins, destinations, max_meters=MAX_METERS, provider=None):
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            return await self.dispatcher.distance_matrix(origins, destinations, session=session, provider=provider)

    def distance_matrix(self, origins, destinations, max_meters=MAX_METERS, provider=None):
        return self.run(
            self.distance_matrix_with_session(origins, destinations, max_meters, provider=provider)
        )

    def __del__(self):
        if self.loop:
            self.loop.stop()
