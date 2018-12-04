import aiohttp
import asyncio
import asyncpg
import os
import numpy as np
import pandas as pd
import ujson
import uvloop
from dataclasses import dataclass
from threading import Thread
from scipy import spatial

from geode import google, dist_metrics
from geode.config import yaml
from geode.cache import PostgresCache
from geode.utils import create_dist_index, KEY_COLS

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

    async def distance_matrix(self, origins, destinations, session=None, provider=None):
        origins = origins.round(4)
        destinations = destinations.round(4)

        client = self.providers.get(provider)

        origins = np.unique(origins, axis=0)
        destinations = np.unique(destinations, axis=0)

        # kick off cache request
        cache_future = asyncio.ensure_future(
            self.cache.get_distances(
                origins, destinations, provider=provider))

        idx = create_dist_index(origins, destinations)

        hdists = spatial.distance.cdist(
            origins,
            destinations,
            dist_metrics.gc_manhattan)

        hdistf = pd.DataFrame(hdists.ravel(), columns=['meters'])
        hdistf['seconds'] = hdistf.meters / 30

        hdistf = pd.concat([idx, hdistf], axis=1)
        hdistf['source'] = 'gc_manhattan'

        # wait on cache request
        distf = await cache_future
        distf_idx = pd.MultiIndex.from_arrays([distf.olat, distf.olon, distf.dlat, distf.dlon])
        distf['source'] = 'google'

        excludes = idx.merge(distf, on=KEY_COLS, how='left').dropna()

        res = await asyncio.gather(*[
            client.distance_matrix(
                origins=[orig],
                destinations=[
                    d for d in destinations[hdists[i] < MAX_METERS]
                    if (orig[0], orig[1], d[0], d[1]) not in distf_idx],
                session=session
            ) for i, orig in enumerate(origins)
        ])

        resdf = None
        flat_res = [row.distances.ravel() for row in res if len(row.distances)]
        if flat_res:
            flatdf = pd.DataFrame.from_records(
                np.concatenate(flat_res)
            )

            valid = [k for k, v in enumerate((hdists < MAX_METERS).flat) if v]

            valid_rows = idx[~idx.index.isin(excludes.index)].reindex(valid).dropna().reset_index(drop=True)
            resdf = pd.concat([valid_rows, flatdf], axis=1)
            resdf['source'] = 'google'

        df = pd.concat([
            hdistf,
            distf,
            resdf
        ], sort=False).drop_duplicates(
            subset=KEY_COLS,
            keep='last')

        df.set_index(
            KEY_COLS,
            drop=True,
            inplace=True)
        df.sort_index(inplace=True)

        await self.cache.set_distances(
            origins, destinations, resdf, provider=provider)

        return df


class Dispatcher:
    cache = None
    cache_conn = None
    providers = {}
    dispatcher = None
    loop = None

    def __init__(self, config=None):
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        loop = asyncio.new_event_loop()

        self.dispatcher = loop.run_until_complete(AsyncDispatcher.init(config))
        self.loop = loop

    async def distance_matrix_with_session(self, origins, destinations, provider=None):
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            return await self.dispatcher.distance_matrix(origins, destinations, session=session, provider=provider)

    def distance_matrix(self, origins, destinations, provider=None):
        return self.loop.run_until_complete(
            self.distance_matrix_with_session(origins, destinations, provider=provider)
        )

    def __del__(self):
        self.loop.stop()
