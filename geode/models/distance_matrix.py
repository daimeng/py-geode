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


class Partition(object):
    def __init__(self, fn):
        self.fn = fn

    def __get__(self, instance, owner):
        return partial(self.__call__, instance)

    async def __call__(self, instance, origins: np.ndarray, destinations: np.ndarray, *args, area_max: int = None,
                       factor_max: int = None, x_max: int = None, y_max: int = None, **kwargs):
        olen = len(origins)
        dlen = len(destinations)

        if olen == 0 or dlen == 0:
            return await self.fn(instance, origins=origins, destinations=destinations, *args, **kwargs)

        # initialize to nans for failure case data
        results = np.full((olen, dlen), np.nan, dtype=distance_matrix.RECORD)

        area_max = area_max or instance.area_max
        factor_max = factor_max or instance.factor_max
        x_max = x_max or instance.x_max
        y_max = y_max or instance.y_max

        chunks = list(partition_matrix(dlen, olen, area_max, factor_max, x_max, y_max))

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


def partition_matrix(xlen: int, ylen: int, area_max: int = None, factor_max: int = None, x_max: int = None, y_max: int = None) -> Iterator[MatrixIterBlock]:
    """
    :param xlen: x length of matrix
    :param ylen: y length of matrix
    :param area_max: x * y <= area_max
    :param factor_max: x + y <= factor_max
    :return: Iterator for sub-matrix rectangles, northwest and southeast corners
    """
    if x_max is None:
        xmax = min(xlen, area_max, factor_max - 1)
    else:
        xmax = x_max

    if y_max is None:
        ymax = min(ylen, area_max // xmax, factor_max - xmax)
    else:
        ymax = y_max

    for y in range(0, ylen, ymax):
        for x in range(0, xlen, xmax):
            x2 = x + xmax - 1
            y2 = y + ymax - 1

            # if partition exceed x bounds
            if x2 > xlen:
                for b in partition_matrix(xlen - x, ylen, area_max, factor_max, x_max, y_max):
                    yield MatrixIterBlock(x + b.x, y + b.y, x + b.x2, y + b.y2)
                xlen = x

            # if partition exceed y bounds
            elif y2 > ylen:
                for b in partition_matrix(xlen, ylen - y, area_max, factor_max, x_max, y_max):
                    yield MatrixIterBlock(x + b.x, y + b.y, x + b.x2, y + b.y2)
                ylen = y

            # partition fits
            else:
                yield MatrixIterBlock(x, y, x2, y2)
