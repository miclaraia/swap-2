
import pickle
import os
import json

from swap.utils.subject import Subjects, ScoreStats, Thresholds
from swap.utils.user import Users
from swap.utils.config import Config
import swap.data

import logging
logger = logging.getLogger(__name__)




class SWAP:

    def __init__(self, config):
        self.name = config.name
        self.users = Users(config)
        self.subjects = Subjects(config)
        self.config = config

        self.thresholds = None
        self._performance = None
        self.last_id = config.last_id


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

    def retire(self):
        fpr = self.config.fpr
        mdr = self.config.mdr
        t = Thresholds(self.subjects, fpr, mdr)
        self.thresholds = t
        bogus, real = t()

        for subject in self.subjects.iter():
            subject.update_score((bogus, real))

    @classmethod
    def load(cls, name):
        conn = swap.data.sqlite()
        conn.row_factory = swap.data.sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT config FROM config WHERE swap=?', (name,))
        config = json.loads(c.fetchone()[0])
        config = Config.load(config)
        swp = SWAP(config)

        def it(rows):
            for item in rows:
                yield dict(item)

        c.execute('SELECT * FROM users where swap=?', (name,))
        swp.users.load(it(c.fetchall()))

        c.execute('SELECT * FROM subjects where swap=?', (name,))
        swp.subjects.load(it(c.fetchall()))

        c.execute('SELECT * FROM thresholds WHERE swap=?', (name,))
        t = c.fetchone()
        if t:
            swp.thresholds = Thresholds.load(swp.subjects, t)

        conn.close()
        return swp

    def save(self):
        conn = swap.data.sqlite()
        c = conn.cursor()
        name = self.config.name
        self.config.last_id = self.last_id

        def zip_name(data):
            return [(name, *d) for d in data]

        swap.data.clear(name, True)
        c.executemany('INSERT INTO users VALUES (?,?,?,?)',
                      zip_name(self.users.dump()))
        c.executemany('INSERT INTO subjects VALUES (?,?,?,?,?,?)',
                      zip_name(self.subjects.dump()))
        if self.thresholds:
            c.execute('INSERT INTO thresholds VALUES (?,?,?,?)',
                      (name, *self.thresholds.dump()))

        c = conn.cursor()
        c.execute('INSERT INTO config VALUES (?,?)',
                  (name, json.dumps(self.config.dump())))
        conn.commit()
        conn.close()



        # data = {
            # 'config': self.config.__dict__,
            # 'users': self.users.dump(),
            # 'subjects': self.subjects.dump(),
            # 'thresholds': thresholds,
            # 'last_id': self.last_id,
        # }

        # fname = self.name + '.pkl'
        # with open(swap.data.path(fname), 'wb') as file:
            # pickle.dump(data, file)

    @property
    def performance(self):
        if self._performance is None:
            self._performance = ScoreStats(self.subjects, self.thresholds)
            self._performance()
        return self._performance
