import numpy as np
from typing import Optional, Tuple

import geode.models as m

from .models import GoogleDistanceMatrixResponse, GoogleDistanceElement, GoogleDistanceElementStatus


def map_from_elm(elm: GoogleDistanceElement) -> Optional[Tuple[int, int]]:
    if elm.status == GoogleDistanceElementStatus.OK:
        return (
            elm.distance.value,
            elm.duration.value
        )
    return None


def map_from_distance_matrix_response(response: GoogleDistanceMatrixResponse) -> np.ndarray:
    dlen = len(response.destination_addresses)
    olen = len(response.origin_addresses)

    results = np.recarray((olen, dlen), dtype=m.distance_matrix.RECORD)

    for y, row in enumerate(response.rows):
        for x, elm in enumerate(row.elements):
            results[y][x] = map_from_elm(elm)

    return results

