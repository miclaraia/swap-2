
import swap.config as config
from swap.caesar.auth import Auth

import logging

logger = logging.getLogger(__name__)


class Address:
    config = config.online_swap

    @classmethod
    def panoptes(cls):
        endpoint = cls.config.caesar.panoptes_endpoint
        url = cls.config.address._panoptes

        return url % {'endpoint': endpoint}

    @classmethod
    def root(cls):
        """
        Returns the root workflow address for caesar
        eg: https://caesar.zooniverse.org:443/workflows/1234
        """
        url = cls.config.address._caesar

        endpoint = cls.config.caesar.caesar_endpoint
        port = cls.config.caesar.port
        workflow = cls.config.workflow
        return url % {'endpoint': endpoint, 'port': port, 'workflow': workflow}

    @classmethod
    def reducer(cls):
        reducer = cls.config.caesar.reducer
        addr = cls.config.address._reducer
        return cls.root() + addr % {'reducer': reducer}

    @classmethod
    def swap_classify(cls):
        addr = cls.config.address._swap
        host = cls.config.host
        port = cls.config.ext_port
        route = cls.config.route

        username = cls.config._auth_username
        password = cls.config._auth_key
        password = Auth._mod_token(password)

        return addr % \
            {'user': username, 'pass': password,
             'host': host, 'port': port, 'route' : route}
