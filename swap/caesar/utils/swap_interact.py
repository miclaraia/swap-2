
import swap.config as config
from swap.utils.scores import Score, ScoreExport
from swap.caesar.utils.requests import Requests
from swap.caesar.utils.caesar_config import CaesarConfig

import json
import logging

logger = logging.getLogger(__name__)


class SwapInteract:

    @classmethod
    def generate_scores(cls):
        user = config.online_swap._auth_username
        key = CaesarConfig.registered_key()

        r = Requests.generate_scores(user, key)
        data = json.loads(r.text)

        logger.debug('Parsed scores for %d subjects', len(data))

        scores = {}
        for item in data['scores'].values():
            item['id_'] = item.pop('id')
            score = Score(**item)
            scores[score.id] = score

        thresholds = tuple(data['thresholds'])

        return ScoreExport(scores, new_golds=False, thresholds=thresholds)
