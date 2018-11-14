import numpy as np # type: ignore
from typing import Optional

import geode.models as m

from .models import GoogleDistanceMatrixResponse, GoogleDistanceElement, GoogleDistanceElementStatus

def map_from_elm(elm: GoogleDistanceElement) -> Optional[m.dist.Entry]:
    if elm.status == GoogleDistanceElementStatus.OK:
        return m.dist.Entry(
            meters=elm.distance.value,
            seconds=elm.duration.value
        )
    return None

def map_from_distance_matrix_response(response: GoogleDistanceMatrixResponse) -> m.dist.Result:
    dlen = len(response.destination_addresses)
    olen = len(response.origin_addresses)

    results = np.empty((olen, dlen), dtype=np.object)

    for y, row in enumerate(response.rows):
        for x, elm in enumerate(row.elements):
            results[y][x] = map_from_elm(elm)

    return m.dist.Result(
        distances=results.flatten().tolist()
    )
