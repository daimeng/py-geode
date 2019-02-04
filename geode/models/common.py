from dataclasses import dataclass
from typing import NamedTuple, Union


class GeoPoint(NamedTuple):
    lat: float
    lon: float


Location = Union[GeoPoint, str]


@dataclass
class Address:
    formatted: str = ''
    unit: str = ''
    street: str = ''
    number: str = ''
    locality: str = ''
    sublocality: str = ''
    county: str = ''
    state: str = ''
    postcode: str = ''
    postcode_ext: str = ''
