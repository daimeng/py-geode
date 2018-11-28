import os
from geode import google
from geode.config import yaml

TYPE_MAP = {
    'google': google,
    # 'alk': alk,
    # 'bing': bing
}

class Dispatcher:
    providers = {}

    def __init__(self, config=None):
        if not config:
            home = os.path.expanduser('~')
            user_config_path = os.path.join(home, '.geode', 'config.yml')
            # local_config_path = os.path.join('geode-config.yml')

            if os.path.exists(user_config_path) and os.path.isfile(user_config_path):
                config = yaml.load(open(user_config_path))

        for k, v in config['providers'].items():
            self.providers[k] = TYPE_MAP[v['type_']].Client(**v)

    async def distance_matrix(self, origins, destinations, session=None, provider=None):
        p = self.providers.get(provider)

        return await p.distance_matrix(origins, destinations, session=session)
