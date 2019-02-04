from typing import List

import geode.models as m
from .models import GoogleAddress, GoogleAddressComponent, GooglePoint, GoogleLocationType


def map_from_address_components(components: List[GoogleAddressComponent]) -> m.Address:
    addr = m.Address()
    for c in components:
        types = c.types
        if 'route' in types:
            addr.street = c.long_name
        elif 'subpremise' in types:
            addr.unit = c.long_name
        elif 'street_number' in types:
            addr.number = c.long_name
        elif 'locality' in types:
            addr.locality = c.long_name
        elif 'sublocality' in types:
            addr.sublocality = c.long_name
        elif 'administrative_area_level_2' in types:
            addr.county = c.long_name
        elif 'administrative_area_level_1' in types:
            addr.state = c.long_name
        elif 'postal_code' in types:
            addr.postcode = c.long_name
        elif 'postal_code_suffix' in types:
            addr.postcode_ext = c.long_name

    return addr


def latlng_to_point(latlng: GooglePoint) -> m.GeoPoint:
    return m.GeoPoint(lat=latlng.lat, lon=latlng.lng)


def map_from_address(address: GoogleAddress) -> m.geocoding.Result:
    addr = map_from_address_components(address.address_components)
    addr.formatted = address.formatted_address

    geometry = address.geometry

    # TODO: Handle cases where exact match found for vague input
    conf = m.geocoding.Confidence.LOW
    prec = m.geocoding.Precision.GEOMETRIC_CENTER
    if geometry.location_type == GoogleLocationType.ROOFTOP:
        prec = m.geocoding.Precision.ROOFTOP
        conf = m.geocoding.Confidence.EXACT
        if address.partial_match:
            conf = m.geocoding.Confidence.PARTIAL

    res = m.geocoding.Result(
        address=addr,
        point=latlng_to_point(geometry.location),
        confidence=conf,
        precision=prec
    )
    return res
