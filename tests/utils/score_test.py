################################################################

from swap.utils.scores import ScoreExport, Score, ScoreIterator, ScoreStats
from swap.utils.golds import GoldGetter
from swap.db.classifications import Classifications
from swap.agents.subject import Subject

from unittest.mock import MagicMock, patch

# pylint: disable=R0201


class TestScoreExport:

    @patch.object(GoldGetter, 'golds', {})
    def test_init(self):
        golds = {1: 0, 2: 0, 3: 1, 4: 1}
        scores = {}
        for i, g in golds.items():
            scores[i] = Score(i, g, i / 10)

        se = ScoreExport(scores, False)
        print(se.scores)

        assert len(se.scores) == 4
        for score in se.scores.values():
            assert score.gold == golds[score.id]
            assert score.p == score.id / 10

    @patch.object(ScoreExport, 'get_real_golds')
    def test_assign_golds(self, mock):
        golds = [1, 1, 0, 0, 1, 1]

        rg = dict([(i, g) for i, g in enumerate(golds)])
        mock.return_value = rg

        scores = dict([(i, Score(i, None, i / 10))
                       for i in range(len(golds))])
        se = ScoreExport(scores, True)
        for score in se.scores.values():
            assert golds[score.id] == score.gold

    def test_counts(self):
        golds = {1: 0, 2: 0, 3: 1, 4: 1, 5: -1, 6: 1}
        scores = dict([(i, Score(i, g, 0)) for i, g in golds.items()])

        se = ScoreExport(scores, False)
        print(se.scores)

        assert se.counts(0) == {-1: 1, 0: 2, 1: 3}

    def test_composition(self):
        golds = {1: 0, 2: 0, 3: 1, 4: 1, 5: -1, 6: 1}
        scores = dict([(i, Score(i, g, 0)) for i, g in golds.items()])

        se = ScoreExport(scores, False)
        print(se.scores)

        assert se.composition(0) == {-1: 1 / 5, 0: 2 / 5, 1: 3 / 5}
        assert False
        # TODO shouldn't be 1/5 for -1

    def test_purity(self):
        golds = {1: 0, 2: 0, 3: 1, 4: 1, 5: -1, 6: 1}
        scores = dict([(i, Score(i, g, 0)) for i, g in golds.items()])

        se = ScoreExport(scores, False)
        print(se.scores)

        assert se.purity(0) == 3 / 5

    def test_builtins(self):
        golds = {1: 0, 2: 0, 3: 1, 4: 1, 5: -1, 6: 1}
        scores = dict([(i, Score(i, g, 0)) for i, g in golds.items()])

        se = ScoreExport(scores, False)
        print(se.scores)

        assert len(se) == 6
        iter(se)

    def test_roc(self):
        golds = {1: 0, 2: 0, 3: 1, 4: 1, 5: 0, 6: 1}
        scores = dict([(i, Score(i, g, 0)) for i, g in golds.items()])

        se = ScoreExport(scores, False)
        print(list(se.roc()))

        for i, item in enumerate(se.roc()):
            g, p = item
            assert g == golds[i + 1]
            assert p == 0

    def test_roc_notgold(self):
        golds = {0: -1, 1: 0, 2: 1}
        scores = dict([(i, Score(i, g, 0)) for i, g in golds.items()])

        se = ScoreExport(scores, False)
        print(list(se.roc()))

        assert len(list(se.roc())) == 2

    # def test_roc_labels(self):
    #     golds = {1: 0, 2: 0, 3: 1, 4: 1, 5: -1, 6: 1}
    #     scores = dict([(i, Score(i, g, 0)) for i, g in golds.items()])
    #
    #     se = ScoreExport(scores, False)
    #
    #     roc = list(se.roc(labels=(2, 3, 4)))
    #     print(roc)

    def test_find_purity(self):
        golds = [0, 0, 0, 0, 1, 1, 1, 1]
        scores = dict([(i, Score(i, g, i / 10))
                       for i, g in enumerate(golds)])
        se = ScoreExport(scores, False)

        p = se.find_purity(0.99)
        print(p)
        assert p == 0.3

    def test_find_purity_2(self):
        golds = [0, 1, 0, 1, 0, 1, 0, 1, 1]
        scores = dict([(i, Score(i, g, i / 10))
                       for i, g in enumerate(golds)])
        se = ScoreExport(scores, False)

        p = se.find_purity(0.99)
        print(p)
        assert p == 0.6

    def test_completeness(self):
        golds = [1, 1, 1, 0, 0, 0, 0, 0, 1, 1]
        scores = dict([(i, Score(i, g, i / 10))
                       for i, g in enumerate(golds)])
        se = ScoreExport(scores, False)
        c = se.completeness(0.5)

        assert c == 0.4

    def test_completeness_2(self):
        scores = [(1, .1), (1, .1), (1, .1), (0, .4),
                  (0, .5), (0, .5), (0, .5), (0, .6),
                  (1, .9), (1, .9)]
        scores = dict([(i, Score(i, gp[0], gp[1]))
                       for i, gp in enumerate(scores)])
        se = ScoreExport(scores, False)
        c = se.completeness(0.5)

        assert c == 0.4


class TestScoreStats:

    def gen_scores(self, scores):
        out = {}
        for i, score in enumerate(scores):
            g, p = score
            score = Score(i, g, p)

            if p < .2 or p > .8:
                score.retired = p

            out[i] = score

        scores = out
        print(scores)
        print(scores[1])
        scores = ScoreExport(scores, False)

        return scores

    def test_stats(self):
        scores = [
            (1, .1),
            (1, .1),
            (1, .1),
            (1, .1),
            (0, .1),
            (0, .1),

            (0, .5),
            (0, .5),
            (1, .5),
            (1, .5),

            (1, .9),
            (1, .9),
            (0, .9),
            (0, .9),
            (0, .9),
            (0, .9)
        ]

        scores = self.gen_scores(scores)
        scores = list(scores.sorted_scores)
        stats = ScoreStats(scores, (.2, .8))

        assert stats.tpr == .25
        assert stats.fpr == .5
        assert stats.tnr == .25
        assert stats.fnr == .5

        assert stats.purity == 1 / 3
        assert stats.retired == .75
        assert stats.retired_correct == .25

        assert stats.completeness == stats.tpr

    def test_counts_left(self):
        scores = [
            (1, .1),
            (1, .1),
            (1, .1),
            (0, .1),
            (0, .1),
            (1, .9),
            (1, .9),
            (1, .9),
            (0, .9),
            (0, .9),
        ]
        scores = self.gen_scores(scores)

        counts = ScoreStats.counts(scores.sorted_scores, 0, .2)

        assert counts == {-1: 0, 0: 2, 1: 3}

    def test_counts_right(self):
        scores = [
            (1, .1),
            (1, .1),
            (1, .1),
            (0, .1),
            (0, .1),
            (1, .9),
            (1, .9),
            (0, .9),
            (0, .9),
            (0, .9),
        ]
        scores = self.gen_scores(scores)

        counts = ScoreStats.counts(scores.sorted_scores, .8, 1)

        assert counts == {-1: 0, 0: 3, 1: 2}

    def test_counts_all(self):
        scores = [
            (1, .1),
            (1, .1),
            (1, .1),
            (0, .1),
            (0, .1),
            (1, .9),
            (1, .9),
            (1, .9),
            (0, .9),
            (0, .9),
        ]
        scores = self.gen_scores(scores)

        counts = ScoreStats.counts(scores.sorted_scores)

        assert counts == {-1: 0, 0: 4, 1: 6}

    def test_stats_str(self):
        scores = [
            (1, .1),
            (1, .1),
            (1, .1),
            (1, .1),
            (0, .1),
            (0, .1),

            (0, .5),
            (0, .5),
            (1, .5),
            (1, .5),

            (1, .9),
            (1, .9),
            (0, .9),
            (0, .9),
            (0, .9),
            (0, .9)
        ]
        scores = self.gen_scores(scores)
        scores = list(scores.sorted_scores)
        stats = ScoreStats(scores, (.2, .8))
        print(stats)

    def test_stats_property(self):
        scores = [
            (1, .1),
            (1, .1),
            (1, .1),
            (1, .1),
            (0, .1),
            (0, .1),

            (0, .5),
            (0, .5),
            (1, .5),
            (1, .5),

            (1, .9),
            (1, .9),
            (0, .9),
            (0, .9),
            (0, .9),
            (0, .9)
        ]
        scores = self.gen_scores(scores)
        stats = scores.stats

        assert stats.tpr == .25
        assert stats.fpr == .5
        assert stats.tnr == .25
        assert stats.fnr == .5

        assert stats.purity == 1 / 3
        assert stats.retired == .75
        assert stats.retired_correct == .25


class TestScoreIterator:
    def test_(self):
        golds = {1: 0, 2: 0, 3: 1, 4: 1, 5: -1, 6: 1}
        scores = dict([(i, Score(i, g, 0)) for i, g in golds.items()])

        si = ScoreIterator(scores, lambda score: score)
        for score in si:
            i = score.id
            id_ = scores[i].id
            gold = scores[i].gold
            p = scores[i].p

            assert score.id == id_
            assert score.gold == gold
            assert score.p == p
