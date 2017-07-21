
from swap.utils import Singleton
import swap.config as config

from panoptes_client.panoptes import Panoptes

from getpass import getpass
import logging
from flask import Response
import threading
import random
import string

logger = logging.getLogger(__name__)


class _Auth:

    def __init__(self, key=None):
        self._username = config.online_swap._auth_username

        if key is None:
            key = self.generate_key()
        self._key = key

    def check_auth(self, username, token):
        return username == self._username and token == self._key

    def http_string(self):
        return '%s:%s@' % (self._username, self._key)

    @staticmethod
    def authenticate():
        """
        Sends a 401 response that enables basic auth
        """
        return Response(
            'Could not verify your access level for that URL.\n'
            'You have to login with proper credentials', 401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'})

    @staticmethod
    def generate_key():
        choice = string.ascii_letters + string.digits
        key = ''.join([random.choice(choice) for n in range(64)])
        logger.warning('Generated key: %s', key)

        return key


class Auth(_Auth, metaclass=Singleton):
    pass


class _AuthCaesar:

    def __init__(self):
        endpoint = config.online_swap.caesar.panoptes_endpoint
        url = config.online_swap.address._panoptes

        endpoint = url % {'endpoint': endpoint}

        self.client = Panoptes(endpoint=endpoint)
        self.lock = threading.Lock()

    @property
    def token(self):
        return self.client.get_bearer_token()

    def login(self):
        with self.lock:
            logger.info('Logging in to panoptes')
            user = input('Username: ')
            password = getpass()

            self.client.login(user, password)
            token = self.client.get_bearer_token()

        print(token)
        return token

    def auth(self, headers=None):
        logger.info('adding authorization header')
        with self.lock:
            if self.token is None:
                raise self.NotLoggedIn
            token = self.token

        if headers is None:
            headers = {}

        headers.update({
            'Authorization': 'Bearer %s' % token
        })

        return headers

    class NotLoggedIn(Exception):
        def __init__(self):
            super().__init__(
                'Need to log in first. Either set panoptes oauth2 bearer '
                'token in config.online_swap.caesar.OAUTH, or try running '
                'app again with --login flag')


class AuthCaesar(_AuthCaesar, metaclass=Singleton):
    pass
