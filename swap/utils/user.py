
from collections import OrderedDict
import json

from swap.utils.collection import Collection


class User:

    def __init__(self, user, username, confusion, config):
        """
        Parameters
        ----------

        confusion: ([0_numer, 1_numer], [0_denom, 1_denom])
        """
        self.id = user
        self.name = username
        self.history = []
        self.config = config

        self.prior = confusion
        self.numer = confusion[0]
        self.denom = confusion[1]

    @classmethod
    def new(cls, user, username, config):
        return cls(user, username, ([0, 0], [0, 0]), config)

    def save(self):
        # save user to file
        pass

    def classify(self, subject, cl):
        # Add classification to history
        self.history.append((subject.id, subject.gold, cl))

    def update_subject(self, subject):
        for i in range(len(self.history)):
            h = self.history[i]
            if h[0] == subject.id:
                self.history[i] = (h[0], subject.gold, h[2])

    @property
    def confusion(self):
        return (self.numer, self.denom)

    @property
    def score(self):
        numer = self.numer
        denom = self.denom

        gamma = self.config.gamma  # defaults to 1
        score = self.config.user_default  # defaults to [.5, .5]

        for i in [0, 1]:
            if denom[i] > 0:
                score[i] = (numer[i]+gamma) / (denom[i]+2*gamma)

        return score

    def update_score(self):
        numer, denom = self.prior

        for _, gold, cl in self.history:
            if gold in [0, 1]:
                denom[gold] += 1
                if gold == cl:
                    numer[gold] += 1

        self.numer = numer
        self.denom = denom
        return self.score

    def dump(self):
        return (self.id, self.name, json.dumps(self.confusion))

    def truncate(self):
        self.prior = self.confusion
        self.history = []

    @classmethod
    def load(cls, data):
        keys = 'user', 'username', 'confusion', 'config'
        data = {k: data[k] for k in keys}
        data['confusion'] = json.loads(data['confusion'])
        return cls(**data)

    def __str__(self):
        return 'id %s name %14s score %s length %d' % \
                (str(self.id), self.name, self.score, sum(self.denom))

    def __repr__(self):
        return str(self)


class Users(Collection):

    def new(self, user):
        return User.new(user, None, self.config)

    def _load_item(self, data):
        return User.load({'config': self.config, **data})
