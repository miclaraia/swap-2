
import swap.config
from swap.caesar.auth import Auth

import logging
from functools import wraps

logger = logging.getLogger(__name__)


def swap_wrapper(func):
    def wrapper(cls, auth=True):
        protocol = cls.config().address._swap_protocol

        route = func(cls)
        root = cls._swap_root()

        if auth:
            auth_string = Auth().http_string()
            root = protocol + auth_string + root
        else:
            root = protocol + root

        address = '%s/%s' % (root, route)
        return address
    return wrapper


class Address:

    @staticmethod
    def config():
        return swap.config.online_swap

    @classmethod
    def panoptes(cls):
        config = cls.config()

        endpoint = config.caesar.panoptes_endpoint
        url = config.address._panoptes

        return url % {'endpoint': endpoint}

    @classmethod
    def root(cls):
        """
        Returns the root workflow address for caesar
        eg: https://caesar.zooniverse.org:443/workflows/1234
        """
        config = cls.config()

        url = config.address._caesar

        endpoint = config.caesar.caesar_endpoint
        port = config.caesar.port
        workflow = config.workflow
        return url % {'endpoint': endpoint, 'port': port, 'workflow': workflow}

    @classmethod
    def reducer(cls):
        config = cls.config()

        reducer = config.caesar.reducer
        addr = config.address._reducer
        return cls.root() + addr % {'reducer': reducer}

    @classmethod
    def _swap_root(cls):
        config = cls.config()

        addr = config.address._swap
        host = config.host
        port = config.ext_port
        project = config.project

        return addr % {'host': host, 'port': port, 'project': project}

    @classmethod
    @swap_wrapper
    def swap_classify(cls, auth=True):
        return 'classify'

    @classmethod
    @swap_wrapper
    def swap_scores(cls, auth=True):
        return 'scores'
