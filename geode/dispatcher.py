import aiohttp
import asyncio
import os
import numpy as np
import pandas as pd
import ujson
from concurrent.futures import ThreadPoolExecutor
from scipy import spatial
from typing import Dict, Any

from geode import google, dist_metrics
from geode.config import yaml
from geode.cache import PostgresCache
from geode.utils import create_dist_index, grouper, KEY_COLS, first_or_none

TYPE_MAP = {
    'google': google,
    # 'alk': alk,
    # 'bing': bing
}


MAX_METERS = 500000
MIN_METERS = 100
MAX_REQUESTS = 20

VEC_DIST = np.vectorize(spatial.distance.euclidean)

class AsyncDispatcher:
    """
    Dispatcher for generic requests.
    Should handle:
    - Registry and configuration of providers
    - Rate limiting
    - Cache logic
    - High level fallback logic
    """
    cache = None
    cache_conn = None
    providers: Dict[str, Any] = {}
    semaphore = None

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

        # initialize cache
        if 'caching' in config:
            self.cache = PostgresCache(**config['caching'])

    @classmethod
    async def init(cls, config=None):
        instance = cls(config)
        if instance.cache:
            instance.cache_conn = await instance.cache.connection()
        return instance

    async def geocode(self, address, sem=None, session=None, provider=None):
        sem = sem or asyncio.BoundedSemaphore(MAX_REQUESTS)

        return await self.throttled_geocode(address, sem, session=session, provider=provider)

    async def throttled_geocode(self, address, sem, session=None, provider=None):
        client = self.providers.get(provider)

        async with sem:
            return await client.geocode(address, session=session)

    async def batch_geocode(self, locations, sem=None, session=None, provider=None):
        sem = sem or asyncio.BoundedSemaphore(MAX_REQUESTS)
        # TODO: check here if client has batch
        return list(map(first_or_none, await asyncio.gather(*[
            self.throttled_geocode(loc, sem, session=session, provider=provider)
            for loc in locations]
        )))

    async def distance_matrix(self, origins, destinations, max_meters=MAX_METERS, sem=None, session=None, provider=None, return_inverse=False):
        sem = sem or asyncio.BoundedSemaphore(MAX_REQUESTS)

        # prepare parameters and indices
        origins, oinv = np.unique(origins.round(4), axis=0, return_inverse=True)
        destinations, dinv = np.unique(destinations.round(4), axis=0, return_inverse=True)

        idx = create_dist_index(origins, destinations)

        # kick off cache request
        if self.cache:
            cache_future = asyncio.ensure_future(
                self.cache.get_distances(
                    origins, destinations, provider=provider
                )
            )

        estimates = spatial.distance.cdist(
            np.radians(origins),
            np.radians(destinations)
        ) * dist_metrics.R_EARTH

        estimate_df = pd.DataFrame(estimates.ravel(), columns=['meters'], index=idx.index)
        estimate_df['seconds'] = estimate_df.meters / 30
        estimate_df['source'] = 'gc_manhattan'

        out_of_range = estimate_df.index[(estimate_df.meters > max_meters) | (estimate_df.meters < MIN_METERS)]

        # wait on cache request
        if self.cache:
            cache_df = await cache_future
            cache_df['source'] = 'google'

            missing = pd.DataFrame(
                index=idx.index.difference(out_of_range).difference(cache_df.index)
            )
        else:
            missing = pd.DataFrame(
                index=idx.index.difference(out_of_range)
            )

        res_df = await self.distance_rows(missing, sem, session=session, provider=provider)

        if self.cache:
            await self.cache.set_distances(
                origins, destinations, res_df, provider=provider
            )

            merged_df = pd.concat([estimate_df, cache_df, res_df], sort=False)
        else:
            merged_df = pd.concat([estimate_df, res_df], sort=False)

        merged_df = merged_df[~merged_df.index.duplicated(keep='last')].reindex(index=idx.index, copy=False)

        if return_inverse:
            return merged_df, oinv.reshape(oinv.size, -1) * np.size(destinations, 0) + dinv

        return merged_df

    async def throttled_distance_matrix(self, origins, destinations, sem, session=None, provider=None):
        client = self.providers.get(provider)

        async with sem:
            return await client.distance_matrix(origins, destinations, session=session)

    async def distance_rows(self, missing, sem, session=None, provider=None):
        odim = [0, 1]
        ddim = [2, 3]
        ogroups = missing.groupby(level=odim, sort=False)
        dgroups = missing.groupby(level=ddim, sort=False)

        if ogroups.ngroups <= dgroups.ngroups:
            # fewer origins, iterate origin-major
            idx = ogroups
            res = await asyncio.gather(*[
                self.throttled_distance_matrix(
                    origins=[o],
                    destinations=ds.index.to_frame(index=False).values[:, ddim],
                    sem=sem,
                    session=session,
                    provider=provider
                ) for o, ds in idx
            ])
        else:
            # fewer destinations, iterate destination-major
            idx = dgroups
            res = await asyncio.gather(*[
                self.throttled_distance_matrix(
                    origins=ds.index.to_frame(index=False).values[:, odim],
                    destinations=[o],
                    sem=sem,
                    session=session,
                    provider=provider
                ) for o, ds in idx
            ])

        res_df = None
        res_flat = [row.distances.ravel() for row in res if len(row.distances)]
        if res_flat:
            res_df = pd.DataFrame.from_records(
                np.concatenate(res_flat),
                # make new index by flat iterate through the groupby index
                index=pd.MultiIndex.from_tuples((d for _, ds in idx for d in ds.index), names=missing.index.names)
            )
            res_df['source'] = 'google'

        return res_df

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

    async def distance_pairs(self, origins, destinations, max_meters=MAX_METERS, sem=None, session=None, provider=None, return_inverse=False):
        sem = sem or asyncio.BoundedSemaphore(MAX_REQUESTS)

        origins = origins.round(4)
        destinations = destinations.round(4)
        locs, inv = np.unique(np.hstack((origins, destinations)), axis=0, return_inverse=True)
        origins = locs[:, 0:2]
        destinations = locs[:, 2:4]

        idx = pd.DataFrame(locs, columns=KEY_COLS).set_index(KEY_COLS)

        if self.cache:
            cache_future = asyncio.ensure_future(
                self.cache.get_distances(
                    origins, destinations, provider=provider, pair=True
                )
            )

        # no vectorized param version of distance functions
        # this replaces cdist euclidean
        estimates = np.sqrt(np.square(
            VEC_DIST(
                np.radians(origins),
                np.radians(destinations)
            )
        ).sum(axis=1)) * dist_metrics.R_EARTH

        estimate_df = pd.DataFrame(estimates, columns=['meters'], index=idx.index)
        estimate_df['seconds'] = estimate_df.meters / 30
        estimate_df['source'] = 'gc_manhattan'

        out_of_range = estimate_df.index[(estimate_df.meters > max_meters) | (estimate_df.meters < MIN_METERS)]

        if self.cache:
            cache_df = await cache_future
            cache_df['source'] = 'google'

            missing = pd.DataFrame(
                index=idx.index.difference(out_of_range).difference(cache_df.index)
            )
        else:
            missing = pd.DataFrame(
                index=idx.index.difference(out_of_range)
            )

        res_df = await self.distance_rows(missing, sem, session=session, provider=provider)

        if self.cache:
            await self.cache.set_distances(
                origins, destinations, res_df, provider=provider
            )

            merged_df = pd.concat([estimate_df, cache_df, res_df], sort=False)
        else:
            merged_df = pd.concat([estimate_df, res_df], sort=False)

        merged_df = merged_df[~merged_df.index.duplicated(keep='last')].reindex(index=idx.index, copy=False)

        if return_inverse:
            return merged_df, inv

        return merged_df


class Dispatcher:
    """Proxy class for easier use in sync environments."""
    cache = None
    cache_conn = None
    providers: Dict[str, Any] = {}
    dispatcher = None

    def __init__(self, config=None, threaded=True):
        self.threaded = threaded
        self.dispatcher = self.run(AsyncDispatcher.init(config))

    def run(self, coro):
        if self.threaded:
            future = ThreadPoolExecutor().submit(asyncio.run, coro)
            return future.result()
        else:
            return asyncio.run(coro)

    # TODO: find way to consolidate these wrappers
    async def distance_matrix_with_session(self, *args, **kwargs):
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            return await self.dispatcher.distance_matrix(*args, **kwargs, session=session)

    async def distance_pairs_with_session(self, *args, **kwargs):
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            return await self.dispatcher.distance_pairs(*args, **kwargs, session=session)

    async def batch_geocode_with_session(self, *args, **kwargs):
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            return await self.dispatcher.batch_geocode(*args, **kwargs, session=session)

    async def geocode_with_session(self, *args, **kwargs):
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            return await self.dispatcher.geocode(*args, **kwargs, session=session)

    def distance_matrix(self, origins, destinations, max_meters=MAX_METERS, provider=None, return_inverse=False) -> pd.DataFrame:
        """
        :param origins: Locations like format [[42.3, -88.7], [40.1, -89.5], ...]
        :param destinations: Locations like format [[42.3, -88.7], [40.1, -89.5], ...]
        :param max_meters: Max distance in meters to send to provider
        :param provider: Service to query
        :param return_inverse: Give back list of indices to re-expand duplicate origin distance pairs.
        :return: origins x destinations distances.
        """
        return self.run(
            self.distance_matrix_with_session(origins, destinations, max_meters, provider=provider, return_inverse=return_inverse)
        )

    def distance_pairs(self, origins, destinations, max_meters=MAX_METERS, provider=None, return_inverse=False) -> pd.DataFrame:
        return self.run(
            self.distance_pairs_with_session(origins, destinations, max_meters, provider=provider, return_inverse=return_inverse)
        )

    def batch_geocode(self, addresses, provider=None):
        return self.run(
            self.batch_geocode_with_session(addresses, provider=provider)
        )

    def geocode(self, address, provider=None):
        return self.run(
            self.geocode_with_session(address, provider=provider)
        )
