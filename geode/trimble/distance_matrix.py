import numpy as np
from typing import Optional, Tuple

import geode.models as m

from .models import TrimbleDistanceMatrixResponse, TrimbleMatrixEntry


def map_from_elm(elm: TrimbleMatrixEntry) -> Optional[Tuple[int, int]]:
    if elm.Success:
        return (
            elm.Distance,
            elm.Time
        )
    return None


def map_from_distance_matrix_response(response: TrimbleDistanceMatrixResponse) -> np.ndarray:
    dlen = len(response.Destinations)
    olen = len(response.Origins)

    results = np.recarray((olen, dlen), dtype=m.distance_matrix.RECORD)

    for y, row in enumerate(response.MatrixInfo):
        for x, elm in enumerate(row):
            results[y][x] = map_from_elm(elm)

    return results

