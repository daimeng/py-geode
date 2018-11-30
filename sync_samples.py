import sys
import os
import time
import prettyprinter # type: ignore
import numpy as np # type: ignore

import geode.models as m
from geode.dispatcher import Dispatcher

prettyprinter.install_extras(include=['dataclasses'])

def main():
    client = Dispatcher()

    s = time.time()

    res = client.distance_matrix(
        origins=np.array([
            (37.1165, -92.2353),
            (34.1368, -94.5823),
            (37.1165, -92.2353)
        ]),
        destinations=np.array([
            (34.1368, -94.5823),
            (36.3408, -96.0384),
            (32.2834, -92.0286),
            (32.2834, -92.0286)
        ]),
        provider='google')

    t = time.time() - s
    prettyprinter.pprint(res)
    print('Duration: %dms' % (t * 1000))

if __name__ == '__main__':
    main()
