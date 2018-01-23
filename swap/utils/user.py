
from collections import OrderedDict


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
        h = None
        i = 0
        for i, h in self.history:
            if h[0] == subject.id:
                break
        self.history[i] = (subject.id, subject.gold, h[2])

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


class Users:

    def __init__(self):
        self.subjects = {}

    def add(self, subject):
        self.subjects[subject.id] = subject

    def iter(self):
        for s in self.subjects:
            yield self.subjects[s]

    def list(self):
        return list(self.subjects.values())

    def __getitem__(self, subject):
        return self.subjects[subject]



