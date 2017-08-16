
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

"""
Classes to manage Authentication when SWAP is running in online mode.
"""


class _Auth:
    """
    Singleton instance to manage how external tools (like Caesar)
    to authenticate with SWAP.
    """

    def __init__(self, key=None):
        self._username = config.online_swap._auth_username

        if key is None:
            key = self.generate_key()
        self._key = key

    def check_auth(self, username, token):
        """
        Verify username and token string are valid
        """
        return username == self._username and token == self._key

    def http_string(self):
        """
        Supply the auth credentials as they should appear in the
        URL given to Caesar
        """
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
        """
        Generate a random string as a token password
        """
        choice = string.ascii_letters + string.digits
        key = ''.join([random.choice(choice) for n in range(64)])
        logger.warning('Generated key: %s', key)

        return key


class Auth(_Auth, metaclass=Singleton):
    pass


class _AuthCaesar:
    """
    Singleton instance to manage how SWAP authenticate with Caesar.

    Uses the Panoptes python client to manage OAuth2 auth. A user
    needs to enter their Zooniverse once on startup. From then on
    the instance uses a Bearer token to authenticate with Caesar, and
    can refresh the token periodically when it expires.
    """

    def __init__(self):
        endpoint = config.online_swap.caesar.panoptes_endpoint
        url = config.online_swap.address._panoptes

        endpoint = url % {'endpoint': endpoint}

        self.client = Panoptes(endpoint=endpoint)
        self.lock = threading.Lock()

    @property
    def token(self):
        """
        Fetch the bearer token from the panoptes python client
        """
        return self.client.get_bearer_token()

    def login(self):
        """
        Prompt the user for their Zooniverse username and password
        and send them to the panoptes python client to log in
        """
        with self.lock:
            logger.info('Logging in to panoptes')
            user = input('Username: ')
            # Hide password entry
            password = getpass()

            self.client.login(user, password)
            token = self.client.get_bearer_token()

        print(token)
        return token

    def auth(self, headers=None):
        # Add an authorization header with the bearer token
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
        """
        Raised if the panoptes client is not logged in
        """
        def __init__(self):
            super().__init__(
                'Need to log in first. Try running again with '
                'the --login flag')


class AuthCaesar(_AuthCaesar, metaclass=Singleton):
    pass
