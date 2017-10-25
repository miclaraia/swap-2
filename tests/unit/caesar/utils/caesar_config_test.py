
import swap.config as config
from swap.caesar.utils.caesar_config import CaesarConfig
from swap.caesar.utils.requests import Requests
from swap.caesar.auth import Auth
from swap.caesar.utils.address import Address

from unittest.mock import patch, MagicMock
import pytest
import json

@patch('swap.config.online_swap._auth_username', 'user')
@pytest.fixture(scope='class')
def auth():
    Auth._reset()
    Auth('123456')

@patch('swap.config.online_swap.workflow', 1234)
@patch('swap.config.online_swap.project', 'project')
@patch('swap.config.online_swap._auth_username', 'user')
@patch('swap.config.online_swap.caesar.caesar_endpoint', 'caesar')
class TestCaesarConfig:

    @patch.object(Requests, 'fetch_caesar_config', MagicMock())
    def test_get_config(self, auth):
        data = {
            'project': 1234,
            'workflow': 5678,
            'created_at': '20170101T10:10:00',
            'extractors_config': {'swap': {'type': 'external'}},
            'reducers_config': {'swap': {'type': 'external'}}
        }

        Requests.fetch_caesar_config().text = json.dumps(data)

        config = CaesarConfig.get_config()
        print(config)
        assert config == {
            'extractors_config': {'swap': {'type': 'external'}},
            'reducers_config': {'swap': {'type': 'external'}}
        }

    @patch.object(Requests, 'fetch_caesar_config', MagicMock())
    @patch.object(Requests, 'put_caesar_config', return_value=MagicMock())
    def test_register_config(self, mock, auth):
        data = {
            'project': 1234,
            'workflow': 5678,
            'created_at': '20170101T10:10:00',
            'extractors_config': {'a': {'type': 'choice'}},
            'reducers_config': {'b': {'type': 'count'}}
        }

        Requests.fetch_caesar_config().text = json.dumps(data)

        address = Address.swap_classify()

        call_data = {
            'extractors_config': {
                'a': {'type': 'choice'},
                'swap': {'type': 'external', 'url': address}
            },
            'reducers_config': {
                'b': {'type': 'count'},
                'swap': {'type': 'external'}
            }
        }

        CaesarConfig.register()

        print(call_data)
        print(mock.call_args[0][0])
        mock.assert_called_with(call_data)

    @patch.object(Requests, 'fetch_caesar_config', MagicMock())
    @patch.object(Requests, 'put_caesar_config', return_value=MagicMock())
    def test_unregister_config(self, mock, auth):
        address = Address.swap_classify()
        data = {
            'project': 1234,
            'workflow': 5678,
            'created_at': '20170101T10:10:00',
            'extractors_config': {
                'a': {'type': 'choice'},
                'swap': {'type': 'external', 'url': address}
            },
            'reducers_config': {
                'b': {'type': 'count'},
                'swap': {'type': 'external'}
            }
        }

        Requests.fetch_caesar_config().text = json.dumps(data)

        call_data = {
            'extractors_config': {'a': {'type': 'choice'}},
            'reducers_config': {'b': {'type': 'count'}}
        }

        CaesarConfig.unregister()

        print(call_data)
        print(mock.call_args[0][0])
        mock.assert_called_with(call_data)

    @patch.object(Requests, 'fetch_caesar_config', MagicMock())
    @patch.object(Requests, 'put_caesar_config', return_value=MagicMock())
    def test_clear_config(self, mock, auth):
        address = Address.swap_classify()
        data = {
            'project': 1234,
            'workflow': 5678,
            'created_at': '20170101T10:10:00',
            'extractors_config': {
                'a': {'type': 'choice'},
                'swap': {'type': 'external', 'url': address}
            },
            'reducers_config': {
                'b': {'type': 'count'},
                'swap': {'type': 'external'}
            }
        }

        Requests.fetch_caesar_config().text = json.dumps(data)

        call_data = {
            'extractors_config': {},
            'reducers_config': {},
            'rules_config': []
        }

        CaesarConfig.clear_all()

        print(call_data)
        print(mock.call_args[0][0])
        mock.assert_called_with(call_data)

    @patch.object(Requests, 'fetch_caesar_config', MagicMock())
    @patch.object(Requests, 'put_caesar_config', return_value=MagicMock())
    def test_clear_rules(self, mock, auth):
        address = Address.swap_classify()
        data = {
            'project': 1234,
            'workflow': 5678,
            'created_at': '20170101T10:10:00',
            'extractors_config': {
                'a': {'type': 'choice'},
                'swap': {'type': 'external', 'url': address}
            },
            'reducers_config': {
                'b': {'type': 'count'},
                'swap': {'type': 'external'}
            },
            'rules_config': [
                {'a rule': []}
            ]
        }

        Requests.fetch_caesar_config().text = json.dumps(data)

        call_data = {
            'rules_config': []
        }

        CaesarConfig.clear_rules()

        print(call_data)
        print(mock.call_args[0][0])
        mock.assert_called_with(call_data)

    @patch.object(Requests, 'fetch_caesar_config', MagicMock())
    def test_is_registered_both(self, auth):
        address = Address.swap_classify()
        data = {
            'project': 1234,
            'workflow': 5678,
            'created_at': '20170101T10:10:00',
            'extractors_config': {
                'a': {'type': 'choice'},
                'swap': {'type': 'external', 'url': address}
            },
            'reducers_config': {
                'b': {'type': 'count'},
                'swap': {'type': 'external'}
            },
            'rules_config': [
                {'a rule': []}
            ]
        }

        Requests.fetch_caesar_config().text = json.dumps(data)

        assert CaesarConfig.is_registered() is True

    @patch.object(Requests, 'fetch_caesar_config', MagicMock())
    def test_is_registered_ext(self, auth):
        address = Address.swap_classify()
        data = {
            'project': 1234,
            'workflow': 5678,
            'created_at': '20170101T10:10:00',
            'extractors_config': {
                'a': {'type': 'choice'},
                'swap': {'type': 'external', 'url': address}
            },
            'reducers_config': {
                'b': {'type': 'count'}
            },
            'rules_config': [
                {'a rule': []}
            ]
        }

        Requests.fetch_caesar_config().text = json.dumps(data)

        assert CaesarConfig.is_registered() is False

    @patch.object(Requests, 'fetch_caesar_config', MagicMock())
    def test_is_registered_red(self, auth):
        address = Address.swap_classify()
        data = {
            'project': 1234,
            'workflow': 5678,
            'created_at': '20170101T10:10:00',
            'extractors_config': {
                'a': {'type': 'choice'}
            },
            'reducers_config': {
                'b': {'type': 'count'},
                'swap': {'type': 'external'}
            },
            'rules_config': [
                {'a rule': []}
            ]
        }

        Requests.fetch_caesar_config().text = json.dumps(data)

        assert CaesarConfig.is_registered() is False

    @patch.object(Requests, 'fetch_caesar_config', MagicMock())
    def test_isnt_registered(self, auth):
        address = Address.swap_classify()
        data = {
            'project': 1234,
            'workflow': 5678,
            'created_at': '20170101T10:10:00',
            'extractors_config': {
                'a': {'type': 'choice'}
            },
            'reducers_config': {
                'b': {'type': 'count'}
            },
            'rules_config': [
                {'a rule': []}
            ]
        }

        Requests.fetch_caesar_config().text = json.dumps(data)

        assert CaesarConfig.is_registered() is False

    @patch.object(Requests, 'fetch_caesar_config', MagicMock())
    @patch.object(Requests, 'put_caesar_config', return_value=MagicMock())
    def test_add_rule(self, mock, auth):
        address = Address.swap_classify()
        data = {
            'project': 1234,
            'workflow': 5678,
            'created_at': '20170101T10:10:00',
            'extractors_config': {
                'a': {'type': 'choice'},
                'swap': {'type': 'external', 'url': address}
            },
            'reducers_config': {
                'b': {'type': 'count'},
                'swap': {'type': 'external'}
            },
            'rules_config': [
                'rule 1'
            ]
        }
        print(data)

        Requests.fetch_caesar_config().text = json.dumps(data)

        call_data = {
            'rules_config': ['rule 1', 'rule 2']
        }

        CaesarConfig.add_rule('rule 2')

        print(call_data)
        print(mock.call_args[0][0])
        mock.assert_called_with(call_data)

    @patch.object(Requests, 'fetch_caesar_config', MagicMock())
    @patch.object(Requests, 'put_caesar_config', return_value=MagicMock())
    def test_fetch_swap_auth_key(self, mock):
        key = 'abcdefghijklmnopqrstuvwxyz'
        Auth._reset()
        Auth(key)

        address = Address.swap_classify()

        data = {
            'extractors_config': {
                'swap': {'type': 'external', 'url': address}
            },
            'reducers_config': {}
        }
        Requests.fetch_caesar_config().text = json.dumps(data)

        assert CaesarConfig.registered_key() == key
