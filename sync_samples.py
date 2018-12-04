import sys
import os
import time
import prettyprinter
import numpy as np

import geode.models as m
from geode.dispatcher import Dispatcher

prettyprinter.install_extras(include=['dataclasses'])

ORIGINS = np.array([
    (37.1165, -92.2353),
    (34.1368, -94.5823),
    (37.1165, -92.2353)
])

DESTS = np.array([
    (34.1368, -94.5823),
    (36.3408, -96.0384),
    (32.2834, -92.0286),
    (32.2834, -92.0286)
])


def main():
    client = Dispatcher()

    s = time.time()

    res = client.distance_matrix(
        origins=np.random.rand(3, 2) * [20, 20] + [25, -100],
        destinations=np.random.rand(4, 2) * [20, 20] + [25, -100],
        provider='google')

    t = time.time() - s
    prettyprinter.pprint(res)
    print('Duration: %dms' % (t * 1000))

if __name__ == '__main__':
    main()
