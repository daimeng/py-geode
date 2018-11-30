import aiohttp
import asyncio
import asyncpg
import os
import pandas as pd
import ujson
from dataclasses import dataclass
from threading import Thread
import uvloop

from geode import google
from geode.config import yaml

TYPE_MAP = {
    'google': google,
    # 'alk': alk,
    # 'bing': bing
}

def CREATE_DISTANCE_TABLE(provider):
    return f'''
CREATE TABLE IF NOT EXISTS distances_{provider} (
    olat decimal(7, 4),
    olon decimal(7, 4),
    dlat decimal(7, 4),
    dlon decimal(7, 4),
    precision smallint,
    meters double precision,
    seconds double precision,
    CONSTRAINT distances_{provider}_pkey PRIMARY KEY (precision, olat, olon, dlat, dlon)
);
CREATE UNIQUE INDEX IF NOT EXISTS distances_{provider}_pkey ON distances_{provider} (precision int2_ops,olat numeric_ops,olon numeric_ops,dlat numeric_ops,dlon numeric_ops);
'''

def CREATE_DISTANCE_TABLE_TEMP(provider):
    return f'''
CREATE TEMPORARY TABLE distances_{provider}_tmp (
    olat decimal(7, 4),
    olon decimal(7, 4),
    dlat decimal(7, 4),
    dlon decimal(7, 4),
    precision smallint,
    meters double precision,
    seconds double precision
);'''


def MERGE_DISTANCES(provider):
    return f'''
INSERT INTO distances_{provider}
	(olat,olon,
    dlat,dlon,
    precision,
    meters,seconds)
	SELECT * FROM distances_{provider}_tmp
ON CONFLICT DO NOTHING;
'''


def GET_DISTANCES(provider):
    return f'''
SELECT * FROM distances_{provider} LIMIT 1;
'''

@dataclass
class PostgresCache:
    host: str
    user: str
    password: str
    database: str

    async def connection(self):
        conn = await asyncpg.connect(user=self.user, password=self.password, database=self.database, host=self.host)

        # TODO: loop thru valid providers
        await conn.execute(CREATE_DISTANCE_TABLE('google'))

        return conn

    async def get_distances(self, origins, destinations):
        conn = await self.connection()
        results = conn.fetch(GET_DISTANCES)

        asyncio.ensure_future(conn.close())

        return pd.DataFrame.from_dict(results)

    async def set_distances(self, origins, destinations, distances, provider):
        conn = await self.connection()

        await conn.execute(CREATE_DISTANCE_TABLE_TEMP(provider))

        df = pd.DataFrame(origins, columns=['olat', 'olon']).assign(k=0).merge(
            pd.DataFrame(destinations, columns=['dlat', 'dlon']).assign(k=0),
            on='k'
        ).drop('k', 1)

        recs = df.merge(
            pd.DataFrame.from_records(distances.flat),
            right_index=True,
            left_index=True
        ).assign(precision=4).drop_duplicates()

        await conn.copy_records_to_table(
            f'distances_{provider}_tmp',
            records=recs.itertuples(index=False),
            columns=[ x for x in recs.columns ]
        )

        await conn.execute(MERGE_DISTANCES(provider))
        await conn.close()

        return

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
        p = self.providers.get(provider)

        result = await p.distance_matrix(origins, destinations, session=session)

        await self.cache.set_distances(
            origins, destinations, result.distances, provider=provider)

        return result


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
