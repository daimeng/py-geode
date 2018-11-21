import dataclasses
import enum
from typing import Any, Dict, Optional, Union

import geode.models as m

def point_to_str(point: m.GeoPoint, precision=4):
    return f'{point[0]:.{precision}},{point[1]:.{precision}}'


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
