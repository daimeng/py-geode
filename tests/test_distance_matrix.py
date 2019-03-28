import numpy as np
import pandas as pd

from geode.dispatcher import Dispatcher


def test_main(mock_server, test_client_config):
    mock_server.reset()
    client = Dispatcher(test_client_config)

    res, inv = client.distance_matrix(
        origins=np.array([[37.1, -88.1],
                          [37.2, -88.2],
                          [42.5, -97.5]]),
        destinations=np.array([[37.1, -88.1],
                               [45.5, -97.5],
                               [37.1, -86.1],
                               [41.9, -97.2]]),
        provider='google',
        return_inverse=True
    )

    assert res.isnull().sum().sum() == 0

    # np.unique will end up sorting index
    pd.testing.assert_index_equal(
        res.index,
        pd.MultiIndex.from_tuples([
            (37.1, -88.1, 37.1, -88.1),
            (37.1, -88.1, 37.1, -86.1),
            (37.1, -88.1, 41.9, -97.2),
            (37.1, -88.1, 45.5, -97.5),

            (37.2, -88.2, 37.1, -88.1),
            (37.2, -88.2, 37.1, -86.1),
            (37.2, -88.2, 41.9, -97.2),
            (37.2, -88.2, 45.5, -97.5),

            (42.5, -97.5, 37.1, -88.1),
            (42.5, -97.5, 37.1, -86.1),
            (42.5, -97.5, 41.9, -97.2),
            (42.5, -97.5, 45.5, -97.5),
        ], names=['olat', 'olon', 'dlat', 'dlon'])
    )

    # double check these values if they should need to change.
    # should be able to eyeball if they look reasonable.
    expected_meters = [
        0.,
        444779.,
        1143293.274236,
        1400881.808377,

        44477.,
        489257.,
        1128289.345949,
        1385191.366365,

        1204670.037841,
        1401763.032474,
        200150.,
        667169.
    ]

    np.testing.assert_array_almost_equal(
        res.meters.values,
        expected_meters
    )

    # restore index with inverse key
    # should be origin-major traversal
    pd.testing.assert_index_equal(
        res.take(inv.flat).index,
        pd.MultiIndex.from_tuples([
            (37.1, -88.1, 37.1, -88.1),
            (37.1, -88.1, 45.5, -97.5),
            (37.1, -88.1, 37.1, -86.1),
            (37.1, -88.1, 41.9, -97.2),

            (37.2, -88.2, 37.1, -88.1),
            (37.2, -88.2, 45.5, -97.5),
            (37.2, -88.2, 37.1, -86.1),
            (37.2, -88.2, 41.9, -97.2),

            (42.5, -97.5, 37.1, -88.1),
            (42.5, -97.5, 45.5, -97.5),
            (42.5, -97.5, 37.1, -86.1),
            (42.5, -97.5, 41.9, -97.2),
        ], names=['olat', 'olon', 'dlat', 'dlon'])
    )
