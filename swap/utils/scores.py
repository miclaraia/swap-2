
from swap.utils.stats import Stat
import swap.config as config
from swap.utils.golds import GoldGetter

import csv

import logging
logger = logging.getLogger(__name__)


class Score:
    """
    Stores information on each subject for export
    """

    def __init__(self, id_, gold, p, n_classifications=None, retired=False):
        """
        Parameters
        ----------
        id_ : int
            Subject id
        gold : gold
            Gold label of subject
        p : float
            SWAP probability that the subject is real
        """
        self.id = id_
        self.gold = gold
        self.p = p
        self.retired = retired
        self.ncl = n_classifications
        self.label = None

    def dict(self):
        return {
            'id': self.id, 'gold': self.gold, 'p': self.p,
            'retired': self.retired, 'ncl': self.ncl}

    @property
    def is_retired(self):
        return self.retired

    def retire(self, p=None):
        if p is not None:
            self.p = p
        self.retired = True

    def __str__(self):
        ncl = self.ncl
        if type(ncl) is float:
            ncl = '%.3f' % ncl

        return 'id: %d gold: %d p: %.4f retired: %s ncl: %s' % \
            (self.id, self.gold, self.p, str(self.retired), ncl)

    def __repr__(self):
        return '{%s}' % self.__str__()


class ScoreExport:
    """
    Export SWAP scores

    Uses less space than pickling and saving the entire SWAP object.
    Used to generate plots like ROC curves.
    """

    def __init__(self, scores,
                 new_golds=True, thresholds=None,
                 gold_getter=None):
        """
        Pararmeters
        -----------
        scores : {Score}
            Mapping of scores in export
        new_golds : bool
            Flag to indicate whether to fetch gold labels from database
            or to use the gold labels already in score objects
        """
        if gold_getter is None:
            gold_getter = GoldGetter()
            gold_getter.all()
        self.gold_getter = gold_getter

        if new_golds:
            scores = self._init_golds(scores)

        self.scores = scores
        self._sorted_ids = sorted(scores, key=lambda id_: scores[id_].p)
        self.class_counts = ScoreStats.counts(self.sorted_scores)

        if thresholds is None:
            thresholds = self.find_thresholds(config.fpr, config.mdr)
        self.thresholds = thresholds

        self._stats = None

    @staticmethod
    def from_csv(fname):
        data = {}

        with open(fname) as csvfile:
            reader = csv.reader(csvfile)
            logger.info('loading csv')

            for i, g, p in reader:
                i = int(i)
                g = int(g)
                p = float(p)
                data[i] = Score(i, g, p)

            logger.info('done')
        return ScoreExport(data, new_golds=False)

    @property
    def sorted_scores(self):
        for i in self._sorted_ids:
            yield self.scores[i]

    @property
    def retired_scores(self):
        for score in self.scores.values():
            if score.is_retired:
                yield score

    @property
    def stats(self):
        if self._stats is None:
            self._stats = self._gen_stats()
        return self._stats

    def _gen_stats(self):
        thresholds = self.thresholds
        return ScoreStats(self, thresholds)

    def _init_golds(self, scores):
        """
        Assign new gold labels to score objects

        Parameters
        ----------
        score : [Score]
            List of scores in export
        """
        golds = self.get_real_golds()
        for score in scores.values():
            if score.id in golds:
                score.gold = golds[score.id]
            else:
                score.gold = -1
        return scores

    def set_retired_flags(self):
        for score in self.sorted_scores:
            bogus, real = self.thresholds
            if score.p < bogus or score.p > real:
                score.retire()

    def get_real_golds(self):
        """
        Fetch gold labels from database
        """
        logger.debug('Getting real gold labels from db')
        return self.gold_getter.golds

    def find_purity(self, desired_purity):
        """
        Determine the threshold for p needed to arrive at the
        desired purity.

        Parameters
        ----------
        desired_purity : float
        """

        def _purity(counts):
            return counts[1] / (counts[1] + counts[0])

        logger.debug('Trying to find purity %.3f', desired_purity)

        counts = self.class_counts.copy()
        for score in self.sorted_scores:
            counts[score.gold] -= 1

            purity = _purity(counts)
            # print(_purity, score, counts)

            if purity is not None and purity > desired_purity:
                logger.info('found purity')
                logger.info('%f %s %s', purity, str(score), str(counts))
                return score.p

        logger.info('Couldn\'t find purity above %f!', desired_purity)
        return 1.0

    def find_thresholds(self, fpr, mdr):
        logger.debug('determining retirement thresholds fpr %.3f mdr %.3f',
                     fpr, mdr)
        totals = self.class_counts.copy()

        # Calculate real retirement threshold
        count = 0
        real = 0
        for score in self.sorted_scores:
            if score.gold == 0:
                count += 1

                _fpr = 1 - count / totals[0]
                # print(_fpr, count, totals[0], score)
                if _fpr < fpr:
                    real = score.p
                    break

        # Calculate bogus retirement threshold
        count = 0
        bogus = 0
        for score in reversed(list(self.sorted_scores)):
            if score.gold == 1:
                count += 1

                _mdr = 1 - count / totals[1]
                # print(_mdr, count, totals[1], score)
                if _mdr < mdr:
                    bogus = score.p
                    break

        logger.debug('bogus %.4f real %.4f', bogus, real)

        return bogus, real

    def __len__(self):
        return len(self.scores)

    def __iter__(self):
        return iter(self.scores)

    def roc(self):
        """
        Generate iterator of information for a ROC curve
        """
        def func(score):
            return score.gold, score.p

        def isgold(score):
            return score.gold in [0, 1]

        scores = list(self.sorted_scores)
        return ScoreIterator(scores, func, isgold)

    def full(self):
        """
        Generate iterator of all information
        """
        def func(score):
            return (score.id, score.gold, score.p)
        return ScoreIterator(list(self.sorted_scores), func)

    def full_dict(self):
        scores = {}
        for i in self.scores:
            score = self.scores[i]
            scores[score.id] = score.dict()

        d = {
            'thresholds': list(self.thresholds),
            'scores': scores
        }

        return d

    def dict(self):
        return self.scores.copy()


class ScoreStats:

    def __init__(self, scores, thresholds):
        stats = self.calculate(scores, thresholds)

        self.tpr = None
        self.tnr = None
        self.fpr = None
        self.fnr = None

        self.purity = None
        self.retired = None
        self.retired_correct = None

        self.ncl_mean = None
        self.ncl_median = None
        self.ncl_stdev = None

        self.__dict__.update(stats)

    @property
    def completeness(self):
        return self.tpr

    @classmethod
    def calculate(cls, scores, thresholds):
        scores_list = list(scores.sorted_scores)
        bogus, real = thresholds
        low = cls.counts(scores_list, 0, bogus)
        high = cls.counts(scores_list, real, 1)
        total = cls.counts(scores_list)

        logger.debug('low %s high %s total %s', low, high, total)

        stats = {
            'tpr': high[1] / total[1],
            'tnr': low[0] / total[0],
            'fpr': high[0] / total[0],
            'fnr': low[1] / total[1],

            'purity': high[1] / cls.total(high),
            'retired': (cls.total(low) + cls.total(high)) / cls.total(total),
            'retired_correct':
                (high[1] + low[0]) /
                (cls.total(low) + cls.total(high)),
        }

        stats.update({
            'completeness': stats['tpr'],
            'mdr': 1 - stats['tpr']
        })

        stats.update(cls.ncl_stats(scores))

        return stats

    @classmethod
    def ncl_stats(cls, scores):
        ncl = []
        for score in scores.retired_scores:
            if score.ncl is not None:
                ncl.append(score.ncl)

        if len(ncl) == 0:
            return {}

        stat = Stat(ncl)
        return {
            'ncl_mean': stat.mean,
            'ncl_median': stat.median,
            'ncl_stdev': stat.stdev
        }

    @staticmethod
    def total(counts):
        return counts[0] + counts[1]

    @staticmethod
    def counts(sorted_scores, left=0, right=1):
        counts = {-1: 0, 0: 0, 1: 0}
        for score in sorted_scores:
            p = score.p
            if score.gold == -1 or p is None or p < left or p > right:
                continue

            counts[score.gold] += 1

        return counts

    def dict(self):
        keys = [
            'tpr', 'tnr', 'fpr', 'fnr',
            'purity', 'retired', 'retired_correct',
            'completeness', 'mdr',
            'ncl_mean', 'ncl_median', 'ncl_stdev']

        data = {}
        for k in keys:
            v = self.__dict__[k]
            if v is not None:
                data[k] = v

        return data

    def __str__(self):
        s = ''
        stats = self.dict()
        for key, value in sorted(stats.items(), key=lambda x: x):
            s += '%s: %.3f ' % (key, value)
        return '{%s}' % s[:-1]


class ScoreIterator:
    """
    Custom iterator to process exported score data
    """

    def __init__(self, scores, func, cond=None):
        if type(scores) is dict:
            scores = list(scores.values())
        if type(scores) is not list:
            raise TypeError('scores type %s not valid!' % str(type(scores)))

        self.scores = scores
        self.func = func
        if cond is None:
            self.cond = lambda item: True
        else:
            self.cond = cond
        self.i = 0

    def _step(self):
        if self.i >= len(self):
            raise StopIteration

        score = self.scores[self.i]
        self.i += 1
        return score

    def next(self):
        score = self._step()

        while not self.cond(score):
            score = self._step()

        obj = self.func(score)
        return obj

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def __len__(self):
        return len(self.scores)
