
import swap.config as config
from swap.caesar.utils.address import Address
from swap.caesar.auth import AuthCaesar

from functools import wraps
import json
import requests
import requests.auth
import logging

logger = logging.getLogger(__name__)


def request_wrapper(func):
    @wraps(func)
    def wrapper(cls, *args, **kwargs):
        r = func(cls, *args, **kwargs)

        if r.status_code not in [200, 204, 203]:
            raise cls.BadResponse(r)
        return r
    return wrapper


class Requests:

    @classmethod
    @request_wrapper
    def put_caesar_config(cls, data):
        """
        Update caesar config data
        """
        address = Address.root()
        headers = cls.headers()

        logger.info('PUT to %s config %s', address, data)

        print(headers)
        r = requests.put(address, headers=headers, json=data)
        logger.info('done')

        return r

    @classmethod
    @request_wrapper
    def fetch_caesar_config(cls):
        """
        Fetch the current config stored in caesar
        """
        address = Address.root()

        logger.info('Fetching current config in caesar')
        logger.info('GET to %s', address)

        headers = cls.headers()
        print(headers)

        r = requests.get(address, headers=headers)
        logger.debug('done')

        return r


    @classmethod
    @request_wrapper
    def respond(cls, subject):
        """
        PUT subject score to Caesar
        """
        c = config.online_swap

        address = Address.reducer()

        body = {
            'reduction': {
                'subject_id': subject.id,
                'data': {
                    c.caesar.field: subject.score
                }
            }
        }

        # address='http://httpbin.org/put'
        logger.info('PUT to %s subject %d score %.4f to caesar',
                    address, subject.id, subject.score)

        headers = cls.headers()
        logger.debug('headers %s', str(headers))

        r = requests.put(address, headers=headers, json=body)
        logger.debug('done')

        return r

    @classmethod
    @request_wrapper
    def generate_scores(cls, user, key):
        address = Address.swap_scores(auth=False)
        auth = requests.auth.HTTPBasicAuth(user, key)

        r = requests.get(address, auth=auth)
        logger.debug('done')

        return  r


    class BadResponse(Exception):
        def __init__(self, response, msg=None):
            try:
                data = json.loads(response.text)
            except json.decoder.JSONDecodeError:
                data = response.text

            status = response.status_code
            logger.error('%d %s\n%s', status, str(response), data)

            super().__init__(msg)

    @staticmethod
    def headers():
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'}

        headers.update(AuthCaesar().auth())
        return headers
