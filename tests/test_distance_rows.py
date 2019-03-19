import aiohttp
import pytest
import numpy as np
from asyncio import BoundedSemaphore

from geode.utils import create_dist_index
from geode.dispatcher import AsyncDispatcher


DESTS = np.array([[37.557996, -97.784471],
                  [34.821800, -92.052100],
                  [31.419600, -83.230200]])

ORIGS = np.array([[32.766200, -83.763700],
                  [37.755600, -96.773100],
                  [35.393400, -95.272200]])

FULL_INDEX = np.array([
    (32.7662, -83.7637, 37.557996, -97.784471),
    (32.7662, -83.7637, 34.8218, -92.0521),
    (32.7662, -83.7637, 31.4196, -83.2302),
    (37.7556, -96.7731, 37.557996, -97.784471),
    (37.7556, -96.7731, 34.8218, -92.0521),
    (37.7556, -96.7731, 31.4196, -83.2302),
    (35.3934, -95.2722, 37.557996, -97.784471),
    (35.3934, -95.2722, 34.8218, -92.0521),
    (35.3934, -95.2722, 31.4196, -83.2302)
])

FULL_RESULTS = np.array([
    4183731., 2300400.,  418115.,  # high, med, low
    268869., 1702349., 4420865.,  # low, med, high
    1040095.,  843235., 3561751.  # med, low, high
])


@pytest.mark.asyncio
async def test_full(mock_server, test_client_config):
    mock_server.reset()
    client = await AsyncDispatcher.init(test_client_config)

    # [0 1 2
    #  3 4 5
    #  6 7 8]
    idx = create_dist_index(ORIGS, DESTS)

    async with aiohttp.ClientSession() as session:
        res = await client.distance_rows(
            missing=idx,
            provider='google',
            session=session,
            # TODO: use default sem for async calls also
            sem=BoundedSemaphore(20)
        )

    assert res.isnull().sum().sum() == 0

    # origin-major order
    np.testing.assert_array_almost_equal(
        res.index.values.tolist(),
        FULL_INDEX
    )

    np.testing.assert_array_almost_equal(
        res.meters.values,
        FULL_RESULTS
    )


@pytest.mark.asyncio
async def test_odd(mock_server, test_client_config):
    mock_server.reset()
    client = await AsyncDispatcher.init(test_client_config)

    idx = create_dist_index(ORIGS, DESTS)

    # [0 _ 2
    #  _ 4 _
    #  6 _ 8]
    # take even indices only
    missing = idx.iloc[range(0, len(idx), 2)]

    async with aiohttp.ClientSession() as session:
        res = await client.distance_rows(
            missing=missing,
            provider='google',
            session=session,
            # TODO: use default sem for async calls also
            sem=BoundedSemaphore(20)
        )

    assert res.isnull().sum().sum() == 0

    np.testing.assert_array_almost_equal(
        res.index.values.tolist(),
        [idx for i, idx in enumerate(FULL_INDEX) if i % 2 == 0]
    )

    np.testing.assert_array_almost_equal(
        res.meters.values,
        [idx for i, idx in enumerate(FULL_RESULTS) if i % 2 == 0]
    )


@pytest.mark.asyncio
async def test_thin(mock_server, test_client_config):
    mock_server.reset()
    client = await AsyncDispatcher.init(test_client_config)

    # [_ 1 2
    #  _ 4 5
    #  _ 7 8]
    # take only last 2 destinations, 3 x 2 query
    idx = create_dist_index(ORIGS, DESTS[[1, 2], :])
    expected = [
        1, 4, 7,    # destination-major order, dest1
        2, 5, 8     # dest2
    ]

    async with aiohttp.ClientSession() as session:
        res = await client.distance_rows(
            missing=idx,
            provider='google',
            session=session,
            # TODO: use default sem for async calls also
            sem=BoundedSemaphore(20)
        )

    assert res.isnull().sum().sum() == 0

    np.testing.assert_array_almost_equal(
        res.index.values.tolist(),
        FULL_INDEX[expected, :]
    )

    np.testing.assert_array_almost_equal(
        res.meters.values,
        FULL_RESULTS[expected]
    )


@pytest.mark.asyncio
async def test_jumbled(mock_server, test_client_config):
    mock_server.reset()
    client = await AsyncDispatcher.init(test_client_config)

    jumble = [8, 0, 7, 1, 6, 2, 5, 3]  # omit 4
    idx = create_dist_index(ORIGS, DESTS).take(jumble)


    # should be ordered origin-major
    # grouped by first occurrence each origin value
    #
    # [0 1 2
    #  3 4 5
    #  6 7 8]
    # 
    # 8 (row3) is first group
    # 0 (row1) is second group
    # 5 (row2) is last group
    expected = [
        8, 7, 6,
        0, 1, 2,
        5, 3
    ]

    async with aiohttp.ClientSession() as session:
        res = await client.distance_rows(
            missing=idx,
            provider='google',
            session=session,
            # TODO: use default sem for async calls also
            sem=BoundedSemaphore(20)
        )

    assert res.isnull().sum().sum() == 0

    np.testing.assert_array_almost_equal(
        res.index.values.tolist(),
        FULL_INDEX[expected, :]
    )

    np.testing.assert_array_almost_equal(
        res.meters.values,
        FULL_RESULTS[expected]
    )
