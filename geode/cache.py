import asyncpg
import pandas as pd
from dataclasses import dataclass
from geode.utils import KEY_COLS


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
    precision smallint DEFAULT '4'::smallint,
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


def GET_DISTANCES(provider, origins, destinations, pair=False):
    if pair:
        return f'''
SELECT * FROM distances_{provider}
WHERE (olat, olon, dlat, dlon) IN ({','.join(f'({o[0]},{o[1]},{d[0]},{d[1]})' for o, d in zip(origins, destinations))});
'''

    return f'''
SELECT * FROM distances_{provider}
WHERE (olat, olon) IN ({','.join(f'({x[0]},{x[1]})' for x in origins)})
AND (dlat, dlon) IN ({','.join(f'({x[0]},{x[1]})' for x in destinations)});
'''


@dataclass
class PostgresCache:
    host: str
    user: str
    password: str
    database: str
    port: int = 5432

    async def connection(self):
        conn = await asyncpg.connect(user=self.user, password=self.password, database=self.database, host=self.host, port=self.port)

        # TODO: loop thru valid providers
        await conn.execute(CREATE_DISTANCE_TABLE('google'))

        return conn

    async def get_distances(self, origins, destinations, provider=None, pair=False):
        conn = await self.connection()
        results = await conn.fetch(GET_DISTANCES(provider, origins, destinations, pair))

        await conn.close()

        distf = pd.DataFrame(
            results,
            columns=[*KEY_COLS, 'precision', 'meters', 'seconds']).drop('precision', 1)
        distf[KEY_COLS] = distf[KEY_COLS].astype(pd.np.float)
        distf.set_index(KEY_COLS, drop=True, inplace=True)

        return distf

    async def set_distances(self, origins, destinations, distances, provider):
        if distances is None or distances.empty:
            return

        distances = distances.drop('source', axis=1).reset_index()

        conn = await self.connection()

        await conn.execute(CREATE_DISTANCE_TABLE_TEMP(provider))

        await conn.copy_records_to_table(
            f'distances_{provider}_tmp',
            records=distances.itertuples(index=False),
            columns=[x for x in distances]
        )

        await conn.execute(MERGE_DISTANCES(provider))
        await conn.close()

        return
