
import pickle
import os

from swap.utils.subject import Subject
from swap.utils.user import User
import swap.data


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


class SWAP:

    def __init__(self, name):
        self.name = name
        self.users = Users()
        self.subjects = Subjects()
        self.cl = []

    def classify_many(self, classifications):
        for user, subject, cl in classifications:
            self.classify(user, subject, cl)

        self.apply_subjects()

    def classify(self, user, subject, cl):
        user = self.users[user]
        subject = self.subjects[subject]

        user.classify(subject, cl)

        def apply():
            subject.classify(user, cl)
        self.cl.append(apply)

    def apply_subjects(self):
        for cl in self.cl:
            cl()
        self.cl = []

    def score_users(self):
        for u in self.users.iter():
            u.update_score()

    def score_subjects(self):
        for s in self.subjects.iter():
            s.update_score()

    def transfer_user_scores(self):
        for u in self.users.iter():
            for subject, _, _ in u.history:
                self.subjects[subject].update_user(u)

    def apply_gold(self, subject, gold):
        subject = self.subjects[subject]
        subject.gold = gold
        for user, _, _ in subject.history:
            self.users[user].update_subject(subject)

    def dump(self):
        data = {
            'users': self.users.dump(),
            'subjects': self.subjects.dump(),
        }

        fname = self.name + '.pkl'
        with open(swap.data.path(fname), 'wb') as file:
            pickle.dump(data, file)

    @classmethod
    def load(cls, name):
        fname = name + '.pkl'

        if os.path.isfile(fname):
            with open(swap.data.path(fname), 'rb') as file:
                data = pickle.load(file)

            swp = SWAP(name)
            swp.users = Users.load(data['users'])
            swp.subjects = Subjects.load(data['subjects'])
        else:
            swp = SWAP(name)
        return swp


class Collection:

    def __init__(self):
        self.items = {}

    def add(self, item):
        self.items[item.id] = item

    def iter(self):
        for i in self.items:
            yield self.items[i]

    def list(self):
        return list(self.items.values())

    def new(self, item):
        pass

    def __getitem__(self, item):
        if item not in self.items:
            self.items[item] = self.new(item)
        return self.items[item]

    def dump(self):
        data = []
        for item in self.items.values():
            data.append(item.dump())

        return data

    @classmethod
    def load(cls, data):
        items = cls()
        for item in data:
            item = cls._load_item(item)
            items.items[item.id] = item
        return items

    @classmethod
    def _load_item(cls, data):
        pass

    def __str__(self):
        return '%d items' % len(self.items)

    def __repr__(self):
        return str(self)


class Subjects(Collection):

    def new(self, subject):
        return Subject.new(subject, -1)

    @classmethod
    def _load_item(cls, data):
        return Subject.load(data)


class Users(Collection):

    def new(self, user):
        return User.new(user, None)

    @classmethod
    def _load_item(cls, data):
        return User.load(data)
