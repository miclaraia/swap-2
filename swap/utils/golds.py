
from swap.db import DB
from swap.db.subjects import SubjectStats
from swap.utils.stats import Stat

from functools import wraps

import logging
logger = logging.getLogger(__name__)

# pylint: disable=R0201

def db_cv():
    return DB().controversial


def _getter(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        getter = lambda: func(self, *args, **kwargs)
        logger.debug('Using getter %s', func)

        self.getters.append(getter)
        self._golds = None

        return getter
    return wrapper


class GoldGetter:
    """
    Compile a set of gold labels given a set of parameters
    """

    def __init__(self):
        self.getters = []
        self._golds = None

    @_getter
    def all(self):
        """
        Get all gold labels
        """
        return DB().golds.get_golds()

    @_getter
    def random(self, size):
        """
        Get a random sample of gold labels

        Parameters
        ----------
        size : int
            Sample size
        """
        logger.debug('Size %d', size)
        return DB().golds.get_random_golds(size)

    @_getter
    def subjects(self, subject_ids):
        """
        Get the gold labels for a set of subjects

        Parameters
        ----------
        subject_ids : list
            List of subject ids (int)
        """
        logger.debug('getting %d subjects', len(subject_ids))
        return DB().golds.get_golds(subject_ids)

    @_getter
    def controversial(self, size):
        """
        Get the gold labels for the most controversial subjects

        Parameters
        ----------
        size : int
            Number of subjects
        """
        logger.debug('Size %d', size)
        subjects = db_cv().get_controversial(size)
        return DB().golds.get_golds(subjects)

    @_getter
    def consensus(self, size):
        """
        Get the gold labels for the most consensus subjects

        Parameters
        ----------
        size : int
            Number of subjects
        """
        logger.debug('Size %d', size)
        subjects = db_cv().get_consensus(size)
        return DB().golds.get_golds(subjects)

    @_getter
    def these(self, golds):
        logger.debug('Size %d', size)
        return golds

    # @_getter
    # def extreme_min(self, n_controv, max_consensus):
    #     def f():
    #         controv = cv.get_controversial(n_controv)
    #         consensus = cv.get_max_consensus(max_consensus)

    #         return db.getExpertGold(controv + consensus)
    #     return f

    # @_getter
    # def extremes(self, n_controv, n_consensus):
    #     def f():
    #         controv = cv.get_controversial(n_controv)
    #         consensus = cv.get_consensus(n_consensus)

    #         return db.getExpertGold(controv + consensus)
    #     return f

    def reset(self):
        """
        Reset the gold getter.

        Clears the set of golds and list of getters.
        """
        self.getters = []
        self._golds = None

    @property
    def golds(self):
        """
        Returns the set of golds. Fetches from database the first
        time and caches for faster recall.
        """
        if self._golds is None:
            if len(self.getters) == 0:
                self.all()

            golds = {}
            for getter in self.getters:
                golds.update(getter())

            self._golds = golds
        return self._golds

    def __iter__(self):
        return self.golds


class GoldStats:

    def __init__(self, golds):
        self._subjects = self._init_subjects(golds)

    def _init_subjects(self, golds):
        subjects = {}
        for id_, gold in golds.items():
            stats = SubjectStats(id_, DB())
            subjects[id_] = self.Subject(id_, gold, stats)

        return subjects

    @property
    def counts(self):
        counts = {0: 0, 1: 0, -1: 0}
        for subject in self.subjects:
            counts[subject.gold] += 1

        return counts

    @property
    def subjects(self):
        for subject in self._subjects.values():
            yield subject

    @property
    def controversial(self):
        # print(self._subjects)
        cv = [s.stats.controversial for s in self.subjects]
        print(cv)
        return Stat(cv)

    @property
    def consensus(self):
        cn = [s.stats.consensus for s in self.subjects]
        return Stat(cn)

    def dict(self):
        counts = self.counts
        return {
            'true': counts[1],
            'false': counts[0],
            'total': len(self),
            'controversial': self.controversial.dict(),
            'consensus': self.consensus.dict(),
        }

    def print_(self):
        print(self)

    def __str__(self):
        s = ''
        s += 'controversial %s\n' % str(self.controversial)
        s += 'consensus     %s\n' % str(self.consensus)
        s += 'true %(true)d false %(false)d total %(total)d' % self.dict()

        return s

    def __len__(self):
        return len(self._subjects)

    class Subject:
        def __init__(self, subject, gold, stats):
            self.id = subject
            self.gold = gold
            self.stats = stats
