
from swap.utils.scores import ScoreIterator, Score, ScoreExport
from swap.utils.golds import GoldGetter


class History:

    def __init__(self, id_, gold, score_history):
        """
        Parameters
        ----------
        id_ : int
            Subject it
        gold : int
            Subject gold label 1, 0, or -1
        scores : list
            List of score history for subject [0.2, 0.1, ...]
        """
        self.id = id_
        self.gold = gold
        self.scores = score_history

    def retire(self, thresholds):
        if thresholds is not None:
            bogus, real = thresholds
            for i, score in enumerate(self.scores):
                if score < bogus or score > real:
                    return i, score
        return ((len(self.scores) - 1), self.scores[-1])


class HistoryExport:

    def __init__(self, history, gold_getter=None):
        """
        Parameters
        ----------
        history : {History}
            Mapping of Subject History to subject id
        """
        self.history = history

        if gold_getter is None:
            gold_getter = GoldGetter()
            gold_getter.all()

        self.gold_getter = gold_getter

    def get(self, id_):
        return self.history[id_]

    def traces(self):

        def func(history):
            return (history.gold, history.scores)

        return ScoreIterator(self.history, func)

    def score_export(self, thresholds=None):
        scores = {}
        for history in self.history.values():
            id_ = history.id
            n, p = history.retire(thresholds)

            score = Score(id_, None, p, n_classifications=n)
            scores[id_] = score

        return ScoreExport(
            scores, gold_getter=self.gold_getter,
            thresholds=thresholds)


    def __iter__(self):

        def func(history):
            return (history.id, history.gold, history.scores)
        return ScoreIterator(self.history, func)
