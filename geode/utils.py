import dataclasses
import enum
import numpy as np
import pandas as pd
from typing import Any, Dict, Optional, Union

import geode.models as m

def point_to_str(point: np.ndarray, precision=4):
    if hasattr(point, 'dtype') and point.dtype.names:
        return f"""{point['lat']:.{precision}f},{point['lon']:.{precision}f}"""

    return f"""{point[0]:.{precision}f},{point[1]:.{precision}f}"""


O_COLS = ['olat', 'olon']
D_COLS = ['dlat', 'dlon']
KEY_COLS = O_COLS + D_COLS

def create_dist_index(origins, destinations):
    df = pd.DataFrame(origins, columns=O_COLS).assign(k=0).merge(
        pd.DataFrame(destinations, columns=D_COLS).assign(k=0),
        on='k'
    ).drop('k', 1)
    df.set_index(KEY_COLS, drop=True, inplace=True)

    return df

class UnionParseException(Exception):
    def __init__(self, wrapped: Exception = None):
        self.wrapped = wrapped


# TODO: extract to separate library and directly parse json string to dataclass
def marshall_to(cls: Any, data: Optional[Any]):
    if data is None:
        return data

    if dataclasses.is_dataclass(cls):
        params = {}
        for field in dataclasses.fields(cls):
            params[field.name] = marshall_to(field.type, data.get(field.name))
        return cls(**params)

    elif hasattr(cls, '__origin__'):
        if cls.__origin__ == list:
            fn = lambda x: marshall_to(cls.__args__[0], x)
            return list(map(fn, data))

        elif cls.__origin__ == Union:
            types = cls.__args__

            last_err = UnionParseException()
            # TODO:more efficient matching
            for t in types:
                try:
                    return marshall_to(t, data)
                except Exception as err: 
                    last_err = UnionParseException(err)

            raise last_err

        return data

    elif issubclass(cls, enum.Enum):
        return cls[data]

    return cls(data)
