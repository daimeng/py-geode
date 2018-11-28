import asyncio
import functools
import datetime
import json
import numpy as np # type: ignore
from dataclasses import dataclass
from typing import List, Union, Sequence, Optional

import geode.models as m
from geode.utils import marshall_to, point_to_str

from .geocoding import map_from_address
from .distance_matrix import map_from_distance_matrix_response
from .models import GoogleGeocodingResponse, GoogleDistanceMatrixResponse

@dataclass
class Client(m.dist.Client, m.geoc.Client):
    type_: str = 'google'
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
        print(f'sent request at {(datetime.datetime.now())}')

        return await session.get(
            self.base_url + path,
            params=dict(
                key=self.key,
                **params
            )
        )

    async def geocode(self, location: m.Location, session=None) -> Optional[m.geoc.Result]:
        if isinstance(location, str):
            res = await self.request(self.geocoding_path, dict(address=location), session=session)
        else:
            res = await self.request(self.geocoding_path, dict(address=point_to_str(location)), session=session)

        data = marshall_to(GoogleGeocodingResponse, await res.json())
        return next(map(map_from_address, data.results), None)

    async def batch_geocode(self, locations: List[m.Location], session=None) -> Sequence[Optional[m.geoc.Result]]:
        return await asyncio.gather(*[self.geocode(loc, session=session) for loc in locations])

    # TODO: allow feeding addresses directly into distance_matrix?
    @m.dist.partition
    @m.dist.dedupe
    async def distance_matrix(self, origins: np.ndarray, destinations: np.ndarray, session=None) -> m.dist.Result:
        res = await self.request(
            self.distance_matrix_path,
            dict(
                origins=self.point_sep.join(map(point_to_str, origins)),
                destinations=self.point_sep.join(map(point_to_str, destinations))
            ),
            session=session)

        data = marshall_to(GoogleDistanceMatrixResponse, await res.json())

        return map_from_distance_matrix_response(data)
