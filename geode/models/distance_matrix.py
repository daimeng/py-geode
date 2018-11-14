import abc
import numpy as np # type: ignore
from dataclasses import dataclass
from functools import partial
from typing import Sequence, Iterable, Optional, NamedTuple, Iterator

from geode.models.common import GeoPoint
from geode.models import distance_matrix


@dataclass
class Entry:
    meters: int
    seconds: int


@dataclass
class Result:
    distances: Sequence[Optional[Entry]]


class Client(abc.ABC):
    async def distance_matrix(self, origins: Iterable[GeoPoint], destinations: Iterable[GeoPoint]) -> Result:
        pass


class Dedupe(object):
    def __init__(self, fn):
        self.fn = fn

    def __get__(self, instance, owner):
        return partial(self.__call__, instance)

    async def __call__(self, origins: Iterable[GeoPoint], destinations: Iterable[GeoPoint], *args, **kwargs) -> distance_matrix.Result:
        # make non-numpy version
        origs, omap = np.unique(origins, axis=0, return_inverse=True)
        dests, dmap = np.unique(destinations, axis=0, return_inverse=True)

        # 1d to 2d
        omap = omap.reshape(omap.size, -1)
        dmap = dmap.reshape(-1, dmap.size)

        # retrieve distances
        deduped_res = await self.fn(origs, dests, *args, **kwargs)

        # apply inverses and de-unique
        return distance_matrix.Result(
            distances=[ deduped_res.distances[idx] for idx in (omap * np.size(dests, 0) + dmap).flat ]
        )


class Partition(object):
    def __init__(self, fn):
        self.fn = fn
    
    def __get__(self, instance, owner):
        return partial(self.__call__, instance)

    async def __call__(self, *args, **kwargs):
        origins = kwargs.pop('origins')
        destinations = kwargs.pop('destinations')

        return await self.fn(*args, origins=origins, destinations=destinations, **kwargs)


class MatrixIterBlock(NamedTuple):
    x: int
    y: int
    x2: int
    y2: int

# area_max: x * y
# factor_max: x + y
def partition_matrix(xlen: int, ylen: int, area_max: int, factor_max: int) -> Iterator[MatrixIterBlock]:
    xmax = min(xlen, area_max, factor_max - 1)
    ymax = min(ylen, area_max // xmax, factor_max - xmax)

    for y in range(0, ylen, ymax):
        for x in range(0, xlen, xmax):
            x2 = x + xmax - 1
            y2 = y + ymax - 1

            # if partition exceed x bounds
            if x2 > xlen:
                for b in partition_matrix(xlen - x, ylen, area_max, factor_max):
                    yield MatrixIterBlock(x + b.x, y + b.y, x + b.x2, y + b.y2)
                xlen = x

            # if partition exceed y bounds
            elif y2 > ylen:
                for b in partition_matrix(xlen, ylen - y, area_max, factor_max):
                    yield MatrixIterBlock(x + b.x, y + b.y, x + b.x2, y + b.y2)
                ylen = y

            # partition fits
            else:
                yield MatrixIterBlock(x, y, x2, y2)


