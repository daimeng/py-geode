from typing import List, Dict, Any

import geode.models as m
from .models import SmartyGeocodingResponse, SmartyComponents
# from .models import GoogleAddress, GoogleAddressComponent, GooglePoint, GoogleLocationType

def from_address_components(c: SmartyComponents) -> m.Address:
    return m.Address(
        unit=c.secondary_number,
        street=c.street_name,
        number=c.primary_number,
        locality=c.city_name,
        state=c.state_abbreviation,
        postcode=c.zipcode,
        postcode_ext=c.plus4_code
    )

def from_response(resp: SmartyGeocodingResponse) -> m.geoc.Result:
    addr = from_address_components(resp.components)

    addr.formatted = ', '.join(filter(None, [resp.delivery_line_1, resp.last_line]))
    addr.county = resp.metadata.county_name

    point = m.GeoPoint(lat=resp.metadata.latitude, lon=resp.metadata.longitude)

    prec = m.geoc.Precision.GEOMETRIC_CENTER
    conf = m.geoc.Confidence.LOW

    res = m.geoc.Result(
        address=addr,
        point=point,
        confidence=conf,
        precision=prec
    )
    return res
