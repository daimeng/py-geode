import pytest
import urllib3
import subprocess
import time


class MockServer:
    def __init__(self):
        self.server = subprocess.Popen(
            ['moogle', '-seclimit', '100', '-elmlimit', '1000'],
            # stdout=subprocess.PIPE,
            # stderr=subprocess.DEVNULL
        )
        # should be very quick to start up
        time.sleep(1)
        self.http = urllib3.PoolManager()

    def reset(self):
        self.http.request('GET', 'http://localhost:8080/reset')

    def step(self, t):
        self.http.request('GET', f'http://localhost:8080/step?t={t}')

    def __del__(self):
        self.server.kill()


@pytest.yield_fixture(scope='session')
def mock_server():
    s = MockServer()
    yield s
    s.server.kill()


@pytest.fixture
def test_client_config():
    return {
        'providers': {
            'google': {
                'type_': 'google',
                'key': 'test123',
                'base_url': 'http://localhost:8080/'
            }
        }
    }
