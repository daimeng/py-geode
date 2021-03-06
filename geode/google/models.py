import enum
from dataclasses import dataclass
from typing import List


# Common Models

@dataclass
class GooglePoint:
    lat: float
    lng: float


class GoogleStatus(enum.Enum):
    OK = 1
    ZERO_RESULTS = 2
    OVER_DAILY_LIMIT = 3
    OVER_QUERY_LIMIT = 4
    MAX_ELEMENTS_EXCEEDED = 5
    REQUEST_DENIED = 6
    INVALID_REQUEST = 7
    UNKNOWN_ERROR = 8


# Geocoding Models

class GoogleLocationType(enum.Enum):
    ROOFTOP = 1
    RANGE_INTERPOLATED = 2
    GEOMETRIC_CENTER = 3
    APPROXIMATE = 4


class GoogleAddressComponentTypes(List[str]):
    pass


@dataclass
class GoogleViewport:
    northeast: GooglePoint
    southwest: GooglePoint


@dataclass
class GoogleGeometry:
    location: GooglePoint
    location_type: GoogleLocationType
    bounds: GoogleViewport
    viewport: GoogleViewport


@dataclass
class GoogleAddressComponent:
    long_name: str
    short_name: str
    types: GoogleAddressComponentTypes


@dataclass
class GoogleAddress:
    address_components: List[GoogleAddressComponent]
    formatted_address: str
    geometry: GoogleGeometry
    partial_match: bool
    place_id: str
    types: GoogleAddressComponentTypes


@dataclass
class GoogleGeocodingResponse:
    results: List[GoogleAddress]
    status: GoogleStatus


# Distance Matrix Models

class GoogleDistanceElementStatus(enum.Enum):
    OK = 1
    NOT_FOUND = 2
    ZERO_RESULTS = 3
    MAX_ROUTE_LENGTH_EXCEEDED = 4


@dataclass
class GoogleDistanceUnit:
    # text: str
    value: int = 0


@dataclass
class GoogleDistanceElement:
    distance: GoogleDistanceUnit  # meters
    duration: GoogleDistanceUnit  # seconds
    status: GoogleDistanceElementStatus


@dataclass
class GoogleDistanceRow:
    elements: List[GoogleDistanceElement]


@dataclass
class GoogleDistanceMatrixResponse:
    destination_addresses: List[str]
    origin_addresses: List[str]
    rows: List[GoogleDistanceRow]
    status: GoogleStatus
