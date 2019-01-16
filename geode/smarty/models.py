import enum
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class SmartyComponents:
    primary_number: str
    secondary_number: str = ''
    secondary_designator: str = ''
    street_name: str
    street_suffix: str
    city_name: str
    default_city_name: str
    state_abbreviation: str
    zipcode: str
    plus4_code: str
    delivery_point: str
    delivery_point_check_digit: str

@dataclass
class SmartyMetadata:
    county_name: str
    longitude: float
    latitude: float
    precision: str
    

@dataclass
class SmartyGeocodingResponse:
    delivery_line_1: str
    last_line: str
    components: SmartyComponents
    metadata: SmartyMetadata

SAMPLE_RESULTS = """{
  "input_id": "0",
  "input_index": 0,
  "candidate_index": 0,
  "delivery_line_1": "500 Rutherford Ave",
  "last_line": "Charlestown MA 02129-1647",
  "delivery_point_barcode": "021291647990",
  "components": {
    "primary_number": "500",
    "street_name": "Rutherford",
    "street_suffix": "Ave",
    "city_name": "Charlestown",
    "default_city_name": "Charlestown",
    "state_abbreviation": "MA",
    "zipcode": "02129",
    "plus4_code": "1647",
    "delivery_point": "99",
    "delivery_point_check_digit": "0"
  },
  "metadata": {
    "record_type": "H",
    "zip_type": "Standard",
    "county_fips": "25025",
    "county_name": "Suffolk",
    "carrier_route": "C016",
    "congressional_district": "07",
    "building_default_indicator": "Y",
    "rdi": "Commercial",
    "elot_sequence": "0046",
    "elot_sort": "A",
    "latitude": 42.38228,
    "longitude": -71.07244,
    "precision": "Zip9",
    "time_zone": "Eastern",
    "utc_offset": -5,
    "dst": true
  },
  "analysis": {
    "dpv_match_code": "D",
    "dpv_footnotes": "AAN1",
    "dpv_cmra": "N",
    "dpv_vacant": "N",
    "active": "N",
    "footnotes": "H#"
  }
}
"""