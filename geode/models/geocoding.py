import abc
import enum
from dataclasses import dataclass
from typing import Optional, Sequence

from geode.models.common import Location, Address, GeoPoint


class Confidence(enum.Enum):
    LOW = 0
    PARTIAL = 1
    EXACT = 2


class Precision(enum.Enum):
    APPROXIMATE = 0
    GEOMETRIC_CENTER = 1
    RANGE_INTERPOLATED = 2
    ROOFTOP = 3

    # @staticmethod
    # def from_address(address: Address):
    #     pass


@dataclass
class Result:
    address: Address
    point: Optional[GeoPoint]
    confidence: Confidence = Confidence.LOW
    precision: Precision = Precision.APPROXIMATE


class Client(abc.ABC):
    @abc.abstractmethod
    async def geocode(self, location: Location) -> Sequence[Result]: pass

    # @abc.abstractmethod
    # async def batch_geocode(self, locations: List[Location]) -> Sequence[Optional[Result]]: pass
