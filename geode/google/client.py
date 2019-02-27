import datetime
import logging
import numpy as np
from dataclasses import dataclass
from typing import Sequence
from tenacity import retry, wait_exponential, retry_if_result

import geode.models as m
from geode.utils import marshall_to, point_to_str
from .distance_matrix import map_from_distance_matrix_response
from .geocoding import map_from_address
from .models import GoogleGeocodingResponse, GoogleDistanceMatrixResponse, GoogleStatus

logger = logging.getLogger()


def is_over_query_limit(x):
    return x.status == GoogleStatus.OVER_QUERY_LIMIT or x.status == GoogleStatus.MAX_ELEMENTS_EXCEEDED


GEOCODE_RETRY = retry(
    wait=wait_exponential(multiplier=0.1, min=0.1, max=2),
    retry=retry_if_result(is_over_query_limit)
)

MATRIX_RETRY = retry(
    wait=wait_exponential(multiplier=0.1, min=0.1, max=2),
    retry=retry_if_result(is_over_query_limit)
)


class Client(m.distance_matrix.Client, m.geocoding.Client):
    type_: str
    base_url: str
    geocoding_path = 'maps/api/geocode/json'
    distance_matrix_path = 'maps/api/distancematrix/json'
    point_sep = '|'
    key: str
    area_max: int
    factor_max: int

    # client_id: str
    # secret: str

    def __init__(
            self,
            type_='google',
            base_url='https://maps.googleapis.com/',
            key='',
            area_max=625,
            factor_max=380,
            geocode_retry=GEOCODE_RETRY,
            matrix_retry=MATRIX_RETRY
    ):
        self.type_ = type_
        self.base_url = base_url
        self.key = key
        self.area_max = area_max
        self.factor_max = factor_max
        self._geocode = geocode_retry(self._geocode)
        self._distance_matrix = matrix_retry(self._distance_matrix)

    async def request(self, path, params, session=None):
        return await session.get(
            self.base_url + path,
            params=dict(
                key=self.key,
                **params
            )
        )

    async def _geocode(self, location: m.Location, session=None) -> GoogleGeocodingResponse:
        if isinstance(location, str):
            res = await self.request(self.geocoding_path, dict(address=location), session=session)
        else:
            res = await self.request(self.geocoding_path, dict(address=point_to_str(location)), session=session)

        return marshall_to(GoogleGeocodingResponse, await res.json())

    async def geocode(self, location: m.Location, session=None) -> Sequence[m.geocoding.Result]:
        data = await self._geocode(location, session)
        return list(map(map_from_address, data.results))

    async def _distance_matrix(self, origins: np.ndarray, destinations: np.ndarray,
                               session=None) -> GoogleDistanceMatrixResponse:
        res = await self.request(
            self.distance_matrix_path,
            dict(
                origins=self.point_sep.join(map(point_to_str, origins)),
                destinations=self.point_sep.join(map(point_to_str, destinations))
            ),
            session=session
        )

        return marshall_to(GoogleDistanceMatrixResponse, await res.json())

    @m.distance_matrix.partition
    async def distance_matrix(self, origins: np.ndarray, destinations: np.ndarray,
                              session=None) -> m.distance_matrix.Result:
        if len(origins) == 0 or len(destinations) == 0:
            return m.distance_matrix.Result(
                origins=origins,
                destinations=destinations,
                distances=np.array([])
            )

        data = await self._distance_matrix(origins, destinations, session)

        result = map_from_distance_matrix_response(data)

        return m.distance_matrix.Result(
            origins=origins,
            destinations=destinations,
            distances=result
        )
