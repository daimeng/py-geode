import abc
import asyncio
import numpy as np # type: ignore
from functools import partial
from dataclasses import dataclass
from typing import Sequence, List, Optional, NamedTuple, Iterator

from geode.models.common import GeoPoint
from geode.models import distance_matrix


RECORD = [('meters', float), ('seconds', float)]

@dataclass
class Result:
    distances: np.ndarray


class Client(abc.ABC):
    async def distance_matrix(self, origins: np.ndarray, destinations: np.ndarray) -> Result:
        pass


class Dedupe(object):
    def __init__(self, fn):
        self.fn = fn

    def __get__(self, instance, owner):
        return partial(self.__call__, instance)

    async def __call__(self, instance, origins: np.ndarray, destinations: np.ndarray, *args, dedupe = True, **kwargs) -> distance_matrix.Result:
        if len(origins) == 0 or len(destinations) == 0:
            return distance_matrix.Result(distances=None)

        if not dedupe:
            return await self.fn(instance, origins, destinations, *args, **kwargs)

        # make non-numpy version
        origs, omap = np.unique(origins, axis=0, return_inverse=True)
        dests, dmap = np.unique(destinations, axis=0, return_inverse=True)

        # 1d to 2d
        omap = omap.reshape(omap.size, -1)
        dmap = dmap.reshape(-1, dmap.size)

        # retrieve distances
        deduped_res = await self.fn(instance, origs, dests, *args, **kwargs)
        dists = deduped_res.distances.ravel()

        # apply inverses and de-unique
        return distance_matrix.Result(
            distances=dists.take(omap * np.size(dests, 0) + dmap)
        )

def dedupe(fn):
    return Dedupe(fn)


class Partition(object):
    def __init__(self, area_max: int, factor_max: int, fn):
        self.area_max = area_max
        self.factor_max = factor_max
        self.fn = fn
    
    def __get__(self, instance, owner):
        return partial(self.__call__, instance)

    async def __call__(self, instance, origins: np.ndarray, destinations: np.ndarray, *args, area_max: int = None, factor_max: int = None, **kwargs):
        olen = len(origins)
        dlen = len(destinations)
        results = np.recarray((olen, dlen), dtype=distance_matrix.RECORD)

        area_max = area_max or self.area_max
        factor_max = factor_max or self.factor_max

        chunks = list(partition_matrix(dlen, olen, area_max, factor_max))

        subresults = await asyncio.gather(*[
            self.fn(instance, origins=origins[y:y2+1], destinations=destinations[x:x2+1], *args, **kwargs)
            for x, y, x2, y2 in chunks])

        for subres, chunk in zip(subresults, chunks):
            x, y, x2, y2 = chunk
            xs = x2 - x + 1
            ys = y2 - y + 1

            results[y:ys, x:xs] = subres.distances

        return distance_matrix.Result(distances=results)


def partition(area_max, factor_max):
    def _inner(fn):
        return Partition(area_max, factor_max, fn)
    return _inner

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
