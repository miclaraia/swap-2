
from collections import OrderedDict

from swap.utils.collection import Collection


class User:

    def __init__(self, user, username, score, history):
        self.id = user
        self.name = username
        self.score = score
        self.history = history

    @classmethod
    def new(cls, user, username):
        return cls(user, username, None, [])

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

    def update_score(self):
        correct = [0, 0]
        seen = [0, 0]
        for _, gold, cl in self.history:
            if gold in [0, 1]:
                seen[gold] += 1
                if gold == cl:
                    correct[gold] += 1

        score = [.5, .5]
        for i in [0, 1]:
            if seen[i] > 0:
                score[i] = correct[i] / seen[i]

        self.score = score
        return score

    def dump(self):
        return OrderedDict([
            ('user', self.id),
            ('username', self.name),
            ('score', self.score),
            ('history', self.history),
        ])

    @classmethod
    def load(cls, data):
        return cls(**data)

    def __str__(self):
        return 'id %d name %14s score %s length %d' % \
                (self.id, self.name, self.score, len(self.history))

    def __repr__(self):
        return str(self)


class Users(Collection):

    def new(self, user):
        return User.new(user, None)

    @classmethod
    def _load_item(cls, data):
        return User.load(data)
