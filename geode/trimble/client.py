import logging
import numpy as np
from typing import Sequence
from tenacity import retry, wait_random_exponential, retry_if_result

import geode.models as m
from geode.utils import marshall_to, point_to_str
# from .distance_matrix import map_from_distance_matrix_response
# from .geocoding import map_from_address
from .models import TrimbleDistanceMatrixResponse

logger = logging.getLogger()


def is_over_query_limit(x):
    return False


# random wait alleviates retry bursts
GEOCODE_RETRY = retry(
    wait=wait_random_exponential(multiplier=0.1, min=0.1, max=2, exp_base=1.5),
    retry=retry_if_result(is_over_query_limit),
)

MATRIX_RETRY = retry(
    wait=wait_random_exponential(multiplier=0.1, min=0.1, max=2, exp_base=1.5),
    retry=retry_if_result(is_over_query_limit),
)


class Client(m.distance_matrix.Client):
    type_: str
    base_url: str
    geocoding_path = 'apis/rest/v1.0/Service.svc/locations'
    distance_matrix_path = 'apis/rest/v1.0/Service.svc/route/matrix'
    point_sep = ';'
    key: str
    area_max: int
    factor_max: int
    o_max: int
    d_max: int

    def __init__(
            self,
            type_='trimble',
            base_url='https://pcmiler.alk.com/',
            key='',
            o_max=10,
            d_max=10,
            geocode_retry=GEOCODE_RETRY,
            matrix_retry=MATRIX_RETRY
    ):
        self.type_ = type_
        self.base_url = base_url
        self.key = key
        self.o_max = o_max
        self.d_max = d_max
        # self._geocode = geocode_retry(self._geocode)
        self._distance_matrix = matrix_retry(self._distance_matrix)

    async def request(self, path, params, session=None):
        return await session.get(
            self.base_url + path,
            params=dict(
                key=self.key,
                **params
            )
        )

    async def _distance_matrix(self, origins: np.ndarray, destinations: np.ndarray,
                               session=None) -> TrimbleDistanceMatrixResponse:
        res = await self.request(
            self.distance_matrix_path,
            dict(
                origins=self.point_sep.join(map(point_to_str, origins)),
                destinations=self.point_sep.join(map(point_to_str, destinations))
            ),
            session=session
        )

        return marshall_to(TrimbleDistanceMatrixResponse, await res.json())

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
