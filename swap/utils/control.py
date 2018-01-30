
import pickle
import os

from swap.utils.subject import Subjects, ScoreStats, Thresholds
from swap.utils.user import Users
import swap.data

import logging
logger = logging.getLogger(__name__)


class Config:

    def __init__(self, **kwargs):
        annotation = {
            'task': 'T1',
            'value_key': None,
            'value_separator': '.',
            'true': [1],
            'false': [0],
        }
        if 'annotation' in kwargs:
            annotation.update(kwargs['annotation'])
        self.annotation = annotation
        self.mdr = kwargs.get('mdr', .1)
        self.fpr = kwargs.get('fpr', .01)

    def dump(self):
        return self.__dict__.copy()

    @classmethod
    def load(cls, dump):
        config = cls()
        config.__dict__.update(dump)
        return config

    def __str__(self):
        return str(self.dump())

    def __repr__(self):
        return str(self)


class SWAP:

    def __init__(self, name, config=None):
        self.name = name
        self.users = Users()
        self.subjects = Subjects()

        if config is None:
            config = Config()
        self.config = config

        self.thresholds = None
        self._performance = None
        self.last_id = None

    @classmethod
    def load(cls, name):
        fname = name + '.pkl'

        if os.path.isfile(fname):
            with open(swap.data.path(fname), 'rb') as file:
                data = pickle.load(file)

            config = Config.load(data['config'])

            swp = SWAP(name, config)
            swp.last_id = data['last_id']
            swp.users = Users.load(data['users'])
            swp.subjects = Subjects.load(data['subjects'])

            if data.get('thresholds'):
                swp.thresholds = Thresholds.load(
                    swp.subjects, data['thresholds'])
        else:
            swp = SWAP(name, config)
        return swp

    def __call__(self):
        print('score users')
        self.score_users()
        print('apply subjects')
        self.apply_subjects()
        print('score_subjects')
        self.score_subjects()

    def classify(self, user, subject, cl, id_):
        if self.last_id is None or id_ > self.last_id:
            self.last_id = id_

        user = self.users[user]
        subject = self.subjects[subject]

        user.classify(subject, cl)
        subject.classify(user, cl)

    def truncate(self):
        self.users.truncate()
        self.subjects.truncate()

    def score_users(self):
        for u in self.users.iter():
            u.update_score()

    def score_subjects(self):
        for s in self.subjects.iter():
            s.update_score()

    def apply_subjects(self):
        for u in self.users.iter():
            for subject, _, _ in u.history:
                self.subjects[subject].update_user(u)

    def apply_gold(self, subject, gold):
        subject = self.subjects[subject]
        subject.gold = gold
        for user, _, _ in subject.history:
            self.users[user].update_subject(subject)

    def apply_golds(self, golds):
        for subject, gold in golds:
            self.apply_gold(subject, gold)

    def retire(self, fpr, mdr):
        t = Thresholds(self.subjects, fpr, mdr)
        self.thresholds = t
        bogus, real = t()

        for subject in self.subjects.iter():
            subject.update_score((bogus, real))

    def save(self):
        if self.thresholds is not None:
            thresholds = self.thresholds.dump()
        else:
            thresholds = None
        data = {
            'config': self.config.dump(),
            'users': self.users.dump(),
            'subjects': self.subjects.dump(),
            'thresholds': thresholds,
            'last_id': self.last_id,
        }

        fname = self.name + '.pkl'
        with open(swap.data.path(fname), 'wb') as file:
            pickle.dump(data, file)

    @property
    def performance(self):
        if self._performance is None:
            self._performance = ScoreStats(self.subjects, self.thresholds)
            self._performance()
        return self._performance
