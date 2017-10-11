
from collections import OrderedDict


class History:

    def __init__(self, id_, score_history):
        self.id = id_
        self.scores = score_history

    def convergence(self, gold):
        end = self.scores[-1][gold]
        def compare(v):
            return abs(v - end) < 1e-9

        for i, score in enumerate(self.scores):
            if compare(score[gold]):
                return i + 1

        return len(self.scores)



class UserHistoryExport:

    def __init__(self, history):
        self.history = history

    @staticmethod
    def parse_user(user):
        history = [t.score for t in user.ledger]
        id_ = user.id

        return History(id_, history)

    @classmethod
    def parse_users(cls, users):
        history = {}
        for user in users:
            h = cls.parse_user(user)
            history[h.id] = h

        return cls(history)

    def max_contributors(self, n):
        history = self.history
        def key(item):
            user, _ = item
            return len(history[user])
        users = sorted(self.history.items(), key=key)
        users = reversed(users[-n:])

        return OrderedDict(users)
