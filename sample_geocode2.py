import time
import prettyprinter

import geode.models as m
from geode.dispatcher import Dispatcher
from geode.utils import addresses_to_df

prettyprinter.install_extras(include=['dataclasses'])


def main():
    client = Dispatcher()

    s = time.time()

    res = client.batch_geocode(
        [
            '500 Rutherford Ave, Charlestown MA',
            'Cake Factory',
            '21 Henr St, Bristol, UK',
            'TD Bank 250 Cambridge Street Boston, MA 02114',
            m.GeoPoint(lon=-94.5823, lat=34.1368)
        ],
        provider='google'
    )

    t = time.time() - s
    # convert to DataFrame
    prettyprinter.pprint(addresses_to_df(res))
    print('Duration: %dms' % (t * 1000))


if __name__ == '__main__':
    main()
