
from collections import OrderedDict
import json

from swap.utils.collection import Collection


import logging
logger = logging.getLogger(__name__)

class Subject:
    """
    Class to track an individual subject, its gold status, and its
    score.
    """

    def __init__(self, subject, gold, config,
                 score=None, seen=0, retired=None):
        self.id = subject
        self.gold = gold
        self.config = config

        score = score or config.p0
        self.prior = score
        self.score = score
        self.seen = seen
        self.history = []
        self.retired = retired

    @classmethod
    def new(cls, subject, gold, config):
        """
        Create a new Subject
        """
        return cls(subject, gold, config)

    def classify(self, user, cl):
        """
        Add a classification to this subject

        Params
        ------

        user: user that made the classification
        cl: classification, 1 or 0
        """
        # Add classification to history
        self.seen += 1
        self.history.append((user.id, user.score, cl))

    def update_user(self, user):
        """
        Update the history of this subject when a user's score has changed
        """
        for i in range(len(self.history)):
            h = self.history[i]
            if h[0] == user.id:
                self.history[i] = (h[0], user.score, h[2])

    def _retire(self, thresholds, score):
        bogus, real = thresholds
        if score < bogus:
            return 0
        elif score > real:
            return 1
        return -1

    def update_score(self, thresholds=None, history=False):
        """
        Recalculate the score for this subject from its stored classification
        history.

        Params
        ------

        thresholds: Also update retirement status of this subject given
                    threshold parameters. (bogus, real)
        history: (bool) Return list of score history
        """
        score = self.prior
        _history = []
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

            if history:
                _history.append(score)

            if thresholds is not None:
                retired = self._retire(thresholds, score)
                if retired in [0, 1]:
                    break

        if thresholds is not None:
            self.retired = self._retire(thresholds, score)
        self.score = score
        if history:
            return score, _history
        return score

    def dump(self):
        """
        Dump this subject
        """
        return self.id, self.gold, self.score, self.retired, self.seen
        # return OrderedDict([
            # ('subject', self.id),
            # ('gold', self.gold),
            # ('score', self.score),
            # #('history', self.history),
            # ('retired', self.retired),
            # ('seen', self.seen),
        # ])

    def truncate(self):
        """
        Clear the history of this subject, and update the prior to the
        current score."""
        self.prior = self.score
        self.history = []

    @classmethod
    def load(cls, data):
        """
        Load a subject from dumped data
        """
        keys = 'subject', 'gold', 'score', 'retired', 'seen', 'config'
        data = {k: data[k] for k in keys}
        return cls(**data)

    def __str__(self):
        return 'id %d gold %d score %.3f length %d' % \
                (self.id, self.gold, self.score, len(self.history))

    def __repr__(self):
        return str(self)


class Subjects(Collection):
    """
    Collection of Subjects
    """

    def new(self, subject):
        """
        Create and return a new Subject
        """
        return Subject.new(subject, -1, self.config)

    def _load_item(self, data):
        return Subject.load({'config': self.config, **data})

    def retired(self):
        """
        Return all retired subjects
        """
        subjects = []
        for subject in self.iter():
            if subject.retired in [0, 1]:
                subjects.append(subject.id)
        return self.subset(subjects)

    def gold(self):
        """
        Return subjects that have a gold label
        """
        subjects = []
        for subject in self.iter():
            if subject.gold in [0, 1]:
                subjects.append(subject.id)
        return self.subset(subjects)


class Thresholds:
    """
    Class to determine retirement thresholds

    Thresholds are determined from the false positive rate (fpr) and the
    missed detection rate (mdr), considering only the subjects with gold
    labels. The bogus retirement threshold is set such that a rate equal
    to mdr of real subjects are mislabeled as bogus. The real retirement
    threshold is set such that a rate equal to fpr of bogus subjects are
    labeled as real.
    """

    def __init__(self, subjects, fpr, mdr, thresholds=None):
        self.subjects = subjects
        self.fpr = fpr
        self.mdr = mdr
        self.thresholds = thresholds

    def dump(self):
        """
        Dump thresholds object
        """
        return self.fpr, self.mdr, json.dumps(self.thresholds)
        # return {
            # 'fpr': self.fpr,
            # 'mdr': self.mdr,
            # 'thresholds': json.dumps(self.thresholds)
        # }

    def __str__(self):
        return str(self.dump())

    def __repr__(self):
        return str(self)

    @classmethod
    def load(cls, subjects, data):
        """
        Load thresholds from dumped data
        """
        keys = 'fpr', 'mdr', 'thresholds'
        data = {k: data[k] for k in keys}
        data['subjects'] = subjects
        data['thresholds'] = json.loads(data['thresholds'])
        return cls(**data)

    def get_scores(self):
        """
        Generate sorted list of subject scores and gold labels
        """
        scores = []
        for subject in self.subjects.iter():
            # if len(subject.history) > 0:
            scores.append((subject.gold, subject.score))

        scores = sorted(scores, key=lambda item: item[1])
        return scores

    def get_counts(self, scores):
        """
        Get number of subjects in each gold label class (-1,0,1)
        """
        counts = {k: 0 for k in [-1, 0, 1]}
        for score in scores:
            counts[score[0]] += 1
        return counts

    def __call__(self):
        """
        Determine retirement tresholds
        """
        if self.thresholds is not None:
            return self.thresholds

        fpr = self.fpr
        mdr = self.mdr

        logger.debug('determining retirement thresholds fpr %.3f mdr %.3f',
                     fpr, mdr)

        scores = self.get_scores()
        totals = self.get_counts(scores)

        # Calculate real retirement threshold
        count = 0
        real = 0
        if totals[0] == 0:
            logger.error('No bogus gold labels!')
            real = 1
            _fpr = None
        else:
            for gold, score in scores:
                if gold == 0:
                    count += 1

                    _fpr = 1 - count / totals[0]
                    # print(_fpr, count, totals[0], score)
                    if _fpr < fpr:
                        real = score
                        break

        # Calculate bogus retirement threshold
        count = 0
        bogus = 0
        if totals[1] == 0:
            logger.error('No real gold labels!')
            bogus = 0
            _mdr = None
        else:
            for gold, score in reversed(scores):
                if gold == 1:
                    count += 1

                    _mdr = 1 - count / totals[1]
                    # print(_mdr, count, totals[1], score)
                    if _mdr < mdr:
                        bogus = score
                        break

        p0 = self.subjects.config.p0
        if bogus >= p0:
            logger.warning('bogus is greater than prior, '
                           'setting bogus threshold to p0')
            bogus = p0

        if real <= p0:
            logger.warning('real is less than prior, '
                           'setting real threshold to p0')
            real = p0

        logger.debug('bogus %.4f real %.4f, fpr %.4f mdr %.4f',
                     bogus, real, _fpr, _mdr)

        self.thresholds = bogus, real
        return self.thresholds


class ScoreStats:

    def __init__(self, subjects, thresholds):
        self.subjects = subjects
        self.thresholds = thresholds

        self.tpr = None
        self.tnr = None
        self.fpr = None
        self.fnr = None
        self.mse = None
        self.mse_t = None
        self.mdr = None

        self.purity = None
        self.retired = None
        self.retired_correct = None

    def __call__(self):
        self.calculate()

    @property
    def completeness(self):
        return self.tpr

    def get_scores(self):
        scores = []
        for subject in self.subjects.iter():
            if subject.gold in [0, 1]:
                scores.append((subject.gold, subject.score))

        scores = sorted(scores, key=lambda item: item[1])
        return scores

    def calculate(self):
        scores = self.get_scores()
        bogus, real = self.thresholds()

        low = self.counts(scores, 0, bogus)
        high = self.counts(scores, real, 1)
        total = self.counts(scores)

        logger.debug('low %s high %s total %s', low, high, total)

        stats = {}

        def divide(n, d):
            if d == 0:
                return None
            return n / d

        self.tpr = divide(high[1], total[1])
        self.tnr = divide(low[0], total[0])
        self.fpr = divide(high[0], total[0])
        self.fnr = divide(low[1], total[1])

        self.purity = divide(high[1], self.total(high))
        self.retired = divide(
            (self.total(low) + self.total(high)), len(self.subjects))
        self.retired_correct = divide(
            (high[1] + low[0]), (self.total(low) + self.total(high)))

        # Calculate mean squared error
        self.mse = self.mean_squared_error(scores)
        self.mse_t = self.mean_squared_error(scores, True)

        # self.completeness = self.tpr
        self.mdr = 1 - self.tpr

        return stats

    def mean_squared_error(self, scores, retirement=False):
        bogus, real = self.thresholds()
        error = 0
        n = 0

        for gold, p in scores:
            if gold in [0, 1]:
                if retirement:
                    if p < bogus:
                        p = 0
                    elif p > real:
                        p = 1

                error += (gold - p) ** 2
                n += 1

        error = error / n
        return error

    @staticmethod
    def total(counts):
        return counts[0] + counts[1]

    @staticmethod
    def counts(scores, left=0, right=1):
        counts = {-1: 0, 0: 0, 1: 0}
        for gold, p in scores:
            if gold == -1 or p is None or p < left or p > right:
                continue

            counts[gold] += 1

        return counts

    def dict(self):
        keys = [
            'tpr', 'tnr', 'fpr', 'fnr', 'mse', 'mse_t',
            'purity', 'retired', 'retired_correct',
            'mdr']

        data = []
        for k in keys:
            v = self.__dict__[k]
            if v is not None:
                data.append((k, v))

        return OrderedDict(data)

    def __str__(self):
        s = ''
        stats = self.dict()
        for key, value in sorted(stats.items(), key=lambda x: x):
            s += '%s: %.3f ' % (key, value)
        return '{%s}' % s[:-1]

    def __repr__(self):
        return str(self)
