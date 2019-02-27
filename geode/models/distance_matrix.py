import abc
import asyncio
import numpy as np
from functools import partial
from dataclasses import dataclass
from typing import NamedTuple, Iterator

from . import distance_matrix

RECORD = [('meters', float), ('seconds', float)]


@dataclass
class Result:
    origins: np.ndarray  # echo
    destinations: np.ndarray  # echo
    distances: np.ndarray


class Client(abc.ABC):
    async def distance_matrix(self, origins: np.ndarray, destinations: np.ndarray) -> Result:
        pass


class Dedupe(object):
    def __init__(self, fn):
        self.fn = fn

    def __get__(self, instance, owner):
        return partial(self.__call__, instance)

    async def __call__(self, instance, origins: np.ndarray, destinations: np.ndarray, *args, dedupe=True,
                       **kwargs) -> distance_matrix.Result:
        if len(origins) == 0 or len(destinations) == 0:
            return distance_matrix.Result(distances=[])

        if not dedupe:
            return await self.fn(instance, origins, destinations, *args, **kwargs)

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
    def __init__(self, fn):
        self.fn = fn

    def __get__(self, instance, owner):
        return partial(self.__call__, instance)

    async def __call__(self, instance, origins: np.ndarray, destinations: np.ndarray, *args, area_max: int = None,
                       factor_max: int = None, **kwargs):
        olen = len(origins)
        dlen = len(destinations)

        if olen == 0 or dlen == 0:
            return await self.fn(instance, origins=origins, destinations=destinations, *args, **kwargs)

        # initialize to nans for failure case data
        results = np.full((olen, dlen), np.nan, dtype=distance_matrix.RECORD)

        area_max = area_max or instance.area_max
        factor_max = factor_max or instance.factor_max

        chunks = list(partition_matrix(dlen, olen, area_max, factor_max))

        subresults = await asyncio.gather(*[
            self.fn(instance, origins=origins[y:y2 + 1], destinations=destinations[x:x2 + 1], *args, **kwargs)
            for x, y, x2, y2 in chunks
        ])

        for subres, chunk in zip(subresults, chunks):
            x, y, x2, y2 = chunk

            if subres.distances.size:
                results[y:y2+1, x:x2+1] = subres.distances

        return distance_matrix.Result(
            origins=origins,
            destinations=destinations,
            distances=results
        )


def partition(fn):
    return Partition(fn)


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
