import asyncio
import datetime
import logging
from dataclasses import dataclass
from typing import List, Sequence, Optional

import geode.models as m
from geode.utils import marshall_to, point_to_str
from .geocoding import map_from_address
from .models import SmartyGeocodingResponse

logger = logging.getLogger()

@dataclass
class Client(m.distance_matrix.Client, m.geocoding.Client):
    type_: str = 'smartys'
    base_url = 'https://maps.googleapis.com/'
    geocoding_path = 'maps/api/geocode/json'
    distance_matrix_path = 'maps/api/distancematrix/json'
    point_sep = '|'
    key: str = ''
    area_max: int = 625
    factor_max: int = 380
    # client_id: str
    # secret: str

    async def request(self, path, params, session=None):
        logger.info(f'sent request at {(datetime.datetime.now())}')

        return await session.get(
            self.base_url + path,
            params=dict(
                key=self.key,
                **params
            )
        )

    async def geocode(self, location: m.Location, session=None) -> Optional[m.geocoding.Result]:
        if isinstance(location, str):
            res = await self.request(self.geocoding_path, dict(address=location), session=session)
        else:
            res = await self.request(self.geocoding_path, dict(address=point_to_str(location)), session=session)

        data = marshall_to(SmartyGeocodingResponse, await res.json())
        return next(map(map_from_address, data.results), None)

    async def batch_geocode(self, locations: List[m.Location], session=None) -> Sequence[Optional[m.geocoding.Result]]:
        return await asyncio.gather(*[self.geocode(loc, session=session) for loc in locations])
