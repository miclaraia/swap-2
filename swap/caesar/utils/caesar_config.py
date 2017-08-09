
from swap.caesar.utils.requests import Requests
from swap.caesar.utils.address import Address
import swap.config

import re
import json
import logging
from functools import wraps

logger = logging.getLogger(__name__)


def put_config(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        config = func(*args, **kwargs)
        Requests.put_caesar_config(config)

    return wrapper


class CaesarConfig:

    keys = ['extractors_config', 'reducers_config']

    @classmethod
    def get_config(cls, keys=None):
        data = Requests.fetch_caesar_config()
        data = json.loads(data.text)

        if type(keys) is str:
            keys = [keys]
        elif keys is None:
            keys = cls.keys

        data = {k: data[k] for k in keys}

        logger.debug('fetched caesar config: %s', data)

        return data

    @classmethod
    @put_config
    def register(cls):
        config = cls.get_config()

        name = swap.config.online_swap.caesar.reducer
        addr = Address.swap_classify()

        config['extractors_config'][name] = {'type': 'external', 'url': addr}
        config['reducers_config'][name] = {'type': 'external'}

        return config

    @classmethod
    @put_config
    def unregister(cls):
        config = cls.get_config()

        name = swap.config.online_swap.caesar.reducer

        for k in cls.keys:
            if name in config[k]:
                config[k].pop(name)

        return config

    @classmethod
    @put_config
    def clear_all(cls):
        keys = cls.keys
        config = {k: {} for k in keys}
        config['rules_config'] = []
        return config

    @classmethod
    @put_config
    def clear_rules(cls):
        return {'rules_config': []}

    @classmethod
    def is_registered(cls):
        config = cls.get_config()

        name = swap.config.online_swap.caesar.reducer

        for k in cls.keys:
            if name not in config[k]:
                return False

        return True

    @classmethod
    @put_config
    def add_rule(cls, rule):
        config = cls.get_config('rules_config')

        key = 'rules_config'
        config = {key: config.get(key, [])}

        config[key].append(rule)
        return config

    @classmethod
    def registered_key(cls):
        config = cls.get_config()
        user = swap.config.online_swap._auth_username

        name = swap.config.online_swap.caesar.reducer
        host = swap.config.online_swap.host

        url = config['extractors_config'][name]['url']

        s = '(?<=%s:).*(?=@%s)' % (user, host)
        key = re.search(s, url).group(0)

        return key
