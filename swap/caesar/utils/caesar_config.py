
from swap.caesar.utils.requests import Requests
from swap.caesar.utils.address import Address

import json
import logging
from functools import wraps

logger = logging.getLogger(__name__)


def put_config(func):
    @wraps(func)
    def wrapper(cls):
        config = func(cls)
        Requests.put_caesar_config(config)

    return wrapper


class CaesarConfig:

    @classmethod
    def get_config(cls):
        data = Requests.fetch_caesar_config()
        data = json.loads(data.text)

        keys = ['extractors_config', 'reducers_config']
        data = {k: data[k] for k in keys}

        logger.debug('fetched caesar config: %s', data)

        return data

    @classmethod
    @put_config
    def register(cls):
        config = cls.get_config()

        name = Address.config.caesar.reducer
        addr = Address.swap_classify()

        config['extractors_config'][name] = {'type': 'external', 'url': addr}
        config['reducers_config'][name] = {'type': 'external'}

        return config

    @classmethod
    @put_config
    def unregister(cls):
        config = cls.get_config()

        name = Address.config.caesar.reducer

        config['extractors_config'].pop(name)
        config['reducers_config'].pop(name)


        return config
