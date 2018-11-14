import abc
import enum
from dataclasses import dataclass
from typing import Optional, Iterable, Sequence

from geode.models.common import Location, Address, GeoPoint


class Confidence(enum.Enum):
    NONE = 0
    LOW = 1
    PARTIAL = 2
    EXACT = 3


@dataclass
class Result:
    address: Address
    point: Optional[GeoPoint]
    confidence: Confidence = Confidence.NONE


class Client(abc.ABC):
    @abc.abstractmethod
    async def geocode(self, location: Location) -> Optional[Result]: pass

    @abc.abstractmethod
    async def batch_geocode(self, locations: Iterable[Location]) -> Sequence[Optional[Result]]: pass
