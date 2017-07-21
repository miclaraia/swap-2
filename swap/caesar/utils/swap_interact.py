
import swap.config as config
from swap.caesar.utils.requests import Requests
from swap.caesar.utils.caesar_config import CaesarConfig

import json


class SwapInteract:

    @classmethod
    def generate_scores(cls):
        user = config.online_swap._auth_username
        key = CaesarConfig.registered_key()

        r = Requests.generate_scores(user, key)
        data = json.loads(r.text)

        print(len(data))
