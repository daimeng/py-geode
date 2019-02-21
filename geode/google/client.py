import datetime
import logging
from dataclasses import dataclass
from typing import Sequence

import numpy as np

import geode.models as m
from geode.utils import marshall_to, point_to_str
from .distance_matrix import map_from_distance_matrix_response
from .geocoding import map_from_address
from .models import GoogleGeocodingResponse, GoogleDistanceMatrixResponse

logger = logging.getLogger()


@dataclass
class Client(m.distance_matrix.Client, m.geocoding.Client):
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
        return await session.get(
            self.base_url + path,
            params=dict(
                key=self.key,
                **params
            )
        )

    async def geocode(self, location: m.Location, session=None) -> Sequence[m.geocoding.Result]:
        if isinstance(location, str):
            res = await self.request(self.geocoding_path, dict(address=location), session=session)
        else:
            res = await self.request(self.geocoding_path, dict(address=point_to_str(location)), session=session)

        data = marshall_to(GoogleGeocodingResponse, await res.json())
        return list(map(map_from_address, data.results))

    @m.distance_matrix.partition
    async def distance_matrix(self, origins: np.ndarray, destinations: np.ndarray, session=None) -> m.distance_matrix.Result:
        if len(origins) == 0 or len(destinations) == 0:
            return m.distance_matrix.Result(
                origins=origins,
                destinations=destinations,
                distances=np.array([])
            )

        res = await self.request(
            self.distance_matrix_path,
            dict(
                origins=self.point_sep.join(map(point_to_str, origins)),
                destinations=self.point_sep.join(map(point_to_str, destinations))
            ),
            session=session)

        data = marshall_to(GoogleDistanceMatrixResponse, await res.json())

        result = map_from_distance_matrix_response(data)

        return m.distance_matrix.Result(
            origins=origins,
            destinations=destinations,
            distances=result
        )
