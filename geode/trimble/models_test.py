import json
import os
from geode.utils import marshall_to, point_to_str
from .models import TrimbleDistanceMatrixResponse, TrimbleMatrixEntry, TrimbleAddress, TrimbleLocation, TrimblePoint

dir_path = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(dir_path, 'sample_matrix_response.json')) as file:
    SAMPLE_MATRIX_RESPONSE = json.load(file)


def test_matrix_response():
    assert marshall_to(TrimbleDistanceMatrixResponse, SAMPLE_MATRIX_RESPONSE) == TrimbleDistanceMatrixResponse(
        Origins=[
            TrimbleLocation(
                Address=TrimbleAddress(
                    StreetAddress='416 Bear Creek Circle',
                    City='Lamar',
                    State='MS',
                    Zip='38642',
                    County='Marshall',
                    Country='United States',
                    SPLC=None,
                    CountryPostalFilter=0,
                    AbbreviationFormat=0,
                    CountryAbbreviation='US'),
                Coords=TrimblePoint(Lat=34.930632, Lng=None),
                Region=4),
            TrimbleLocation(
                Address=TrimbleAddress(
                    StreetAddress='1260 Bluntzer Road',
                    City='Goliad',
                    State='TX',
                    Zip='77963',
                    County='Goliad',
                    Country='United States',
                    SPLC=None,
                    CountryPostalFilter=0,
                    AbbreviationFormat=0,
                    CountryAbbreviation='US'),
                Coords=TrimblePoint(Lat=28.883464, Lng=None),
                Region=4),
            TrimbleLocation(
                Address=TrimbleAddress(
                    StreetAddress='Phillips Oil Field Road',
                    City='Cameron',
                    State='LA',
                    Zip='70631',
                    County='Cameron',
                    Country='United States',
                    SPLC=None,
                    CountryPostalFilter=0,
                    AbbreviationFormat=0,
                    CountryAbbreviation='US'),
                Coords=TrimblePoint(Lat=29.757106, Lng=None),
                Region=4),
            TrimbleLocation(
                Address=TrimbleAddress(
                    StreetAddress='3594 West Co Rd 250 South ',
                    City='Cory',
                    State='IN',
                    Zip='47846',
                    County='Clay',
                    Country='United States',
                    SPLC=None,
                    CountryPostalFilter=0,
                    AbbreviationFormat=0,
                    CountryAbbreviation='US'),
                Coords=TrimblePoint(Lat=39.352094, Lng=None),
                Region=4),
            TrimbleLocation(
                Address=TrimbleAddress(
                    StreetAddress='1820 Route 80',
                    City='Plainview',
                    State='TX',
                    Zip='79072',
                    County='Hale',
                    Country='United States',
                    SPLC=None,
                    CountryPostalFilter=0,
                    AbbreviationFormat=0,
                    CountryAbbreviation='US'),
                Coords=TrimblePoint(Lat=34.20324, Lng=None),
                Region=4)
        ],
        Destinations=[
            TrimbleLocation(
                Address=TrimbleAddress(
                    StreetAddress='22150 South Peace Road',
                    City='Arlington',
                    State='KS',
                    Zip='67514',
                    County='Reno',
                    Country='United States',
                    SPLC=None,
                    CountryPostalFilter=0,
                    AbbreviationFormat=0,
                    CountryAbbreviation='US'),
                Coords=TrimblePoint(Lat=37.798421, Lng=None),
                Region=4),
            TrimbleLocation(
                Address=TrimbleAddress(
                    StreetAddress='1681 2500 North',
                    City='Arthur',
                    State='IL',
                    Zip='61911',
                    County='Douglas',
                    Country='United States',
                    SPLC=None,
                    CountryPostalFilter=0,
                    AbbreviationFormat=0,
                    CountryAbbreviation='US'),
                Coords=TrimblePoint(Lat=39.770106, Lng=None),
                Region=4),
            TrimbleLocation(
                Address=TrimbleAddress(
                    StreetAddress='Route 96',
                    City='Briggsdale',
                    State='CO',
                    Zip='80611',
                    County='Weld',
                    Country='United States',
                    SPLC=None,
                    CountryPostalFilter=0,
                    AbbreviationFormat=0,
                    CountryAbbreviation='US'),
                Coords=TrimblePoint(Lat=40.686775, Lng=None),
                Region=4),
            TrimbleLocation(
                Address=TrimbleAddress(
                    StreetAddress='',
                    City='Potts Camp',
                    State='MS',
                    Zip='38659',
                    County='Marshall',
                    Country='United States',
                    SPLC=None,
                    CountryPostalFilter=0,
                    AbbreviationFormat=0,
                    CountryAbbreviation='US'),
                Coords=TrimblePoint(Lat=34.651448, Lng=None),
                Region=4),
            TrimbleLocation(
                Address=TrimbleAddress(
                    StreetAddress='',
                    City='Elkhart',
                    State='KS',
                    Zip='67950',
                    County='Morton',
                    Country='United States',
                    SPLC=None,
                    CountryPostalFilter=0,
                    AbbreviationFormat=0,
                    CountryAbbreviation='US'),
                Coords=TrimblePoint(Lat=37.009147, Lng=None),
                Region=4)
        ],
        MatrixInfo=[
            [
                TrimbleMatrixEntry(
                    Success=True, Errors=[], Time='11:47:45', Distance=712.0),
                TrimbleMatrixEntry(
                    Success=True, Errors=[], Time='09:58:44', Distance=535.07),
                TrimbleMatrixEntry(
                    Success=True, Errors=[], Time='20:15:00', Distance=1189.01),
                TrimbleMatrixEntry(
                    Success=True, Errors=[], Time='01:17:20', Distance=74.62),
                TrimbleMatrixEntry(
                    Success=True, Errors=[], Time='13:36:18', Distance=818.0)
            ],
            [
                TrimbleMatrixEntry(
                    Success=True, Errors=[], Time='11:22:51', Distance=710.87),
                TrimbleMatrixEntry(
                    Success=True, Errors=[], Time='21:07:55', Distance=1216.81),
                TrimbleMatrixEntry(
                    Success=True, Errors=[], Time='18:45:32', Distance=1087.87),
                TrimbleMatrixEntry(
                    Success=True, Errors=[], Time='12:50:06', Distance=753.44),
                TrimbleMatrixEntry(
                    Success=True, Errors=[], Time='12:48:28', Distance=757.06)
            ],
            [
                TrimbleMatrixEntry(
                    Success=True, Errors=[], Time='12:03:00', Distance=742.49),
                TrimbleMatrixEntry(
                    Success=True, Errors=[], Time='19:04:22', Distance=1051.2),
                TrimbleMatrixEntry(
                    Success=True, Errors=[], Time='20:26:16', Distance=1212.64),
                TrimbleMatrixEntry(
                    Success=True, Errors=[], Time='10:16:12', Distance=570.95),
                TrimbleMatrixEntry(
                    Success=True, Errors=[], Time='13:47:34', Distance=841.64)
            ],
            [
                TrimbleMatrixEntry(
                    Success=True, Errors=[], Time='15:42:18', Distance=912.26),
                TrimbleMatrixEntry(
                    Success=True, Errors=[], Time='03:00:21', Distance=149.54),
                TrimbleMatrixEntry(
                    Success=True, Errors=[], Time='00:35:27', Distance=1416.33),
                TrimbleMatrixEntry(
                    Success=True, Errors=[], Time='08:18:25', Distance=442.31),
                TrimbleMatrixEntry(
                    Success=True, Errors=[], Time='19:16:40', Distance=1165.11)
            ],
            [
                TrimbleMatrixEntry(
                    Success=True, Errors=[], Time='07:15:14', Distance=414.96),
                TrimbleMatrixEntry(
                    Success=True, Errors=[], Time='21:57:36', Distance=1311.77),
                TrimbleMatrixEntry(
                    Success=True, Errors=[], Time='09:45:00', Distance=555.0),
                TrimbleMatrixEntry(
                    Success=True, Errors=[], Time='14:02:56', Distance=852.62),
                TrimbleMatrixEntry(
                    Success=True, Errors=[], Time='03:47:52', Distance=224.19)
            ]
        ]
    )
