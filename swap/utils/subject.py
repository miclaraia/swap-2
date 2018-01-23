
from collections import OrderedDict


class Subject:

    def __init__(self, subject, gold, score, history):
        self.id = subject
        self.gold = gold
        self.score = score
        self.history = history

    @classmethod
    def new(cls, subject, gold):
        return cls(subject, gold, .12, [])

    def classify(self, user, cl):
        # Add classification to history
        self.history.append((user.id, user.score, cl))

    def update_user(self, user):
        h = None
        i = 0
        for i, h in self.history:
            if h[0] == user.id:
                break
        self.history[i] = (user.id, user.score, h[2])

    def update_score(self):
        score = self.score
        for _, (u0, u1), cl in self.history:
            if cl == 1:
                a = score * u1
                b = (1-score) * (1-u0)
            elif cl == 0:
                a = score*(1-u1)
                b = (1-score)*(u0)

            try:
                score = a / (a + b)
            # leave score unchanged
            except ZeroDivisionError as e:
                print(e)

        self.score = score
        return score

    def dump(self):
        return OrderedDict([
            ('subject', self.id),
            ('gold', self.gold),
            ('score', self.score),
            ('history', self.history),
        ])

    @classmethod
    def load(cls, data):
        return cls(**data)

    def __str__(self):
        return 'id %d gold %d score %.3f length %d' % \
                (self.id, self.gold, self.score, len(self.history))

    def __repr__(self):
        return str(self)


class Subjects:

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
        if subject not in self.subjects:
            self.subjects[subject] = Subject.new(subject, -1)
        return self.subjects[subject]


