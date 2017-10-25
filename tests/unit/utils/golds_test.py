
from swap.utils.golds import GoldStats

from unittest.mock import MagicMock, patch

Subject = GoldStats.Subject


def init_subjects():
    data = [
        (1, 40, 5),
        (1, 35, 10),
        (1, 30, 15),
        (1, 25, 20),
        (0, 20, 25),
        (0, 20, 30),
        (0, 20, 35),
        (0, 20, 40),
    ]

    subjects = {}
    for i, j in enumerate(data):
        g, cv, cn = j
        stats = init_stats(cv, cn)
        subjects[i] = Subject(i, g, stats)

    return subjects


def init_stats(cv, cn):
    def dict(self):
        return {
            'controversial': cv,
            'consensus': cn
        }
    mock = MagicMock()
    mock.dict = dict
    mock.controversial = cv
    mock.consensus = cn

    return mock


class TestGoldStats:

    @patch.object(GoldStats, '_init_subjects',
                  MagicMock(return_value=init_subjects()))
    def test_counts(self):
        gs = GoldStats([])
        assert gs.counts == {0: 4, 1: 4, -1: 0}

    @patch.object(GoldStats, '_init_subjects',
                  MagicMock(return_value=init_subjects()))
    def test_controversial(self):
        gs = GoldStats([])
        stat = gs.controversial

        assert stat.mean == 26.25
        assert stat.median == 22.5

    @patch.object(GoldStats, '_init_subjects',
                  MagicMock(return_value=init_subjects()))
    def test_consensus(self):
        gs = GoldStats([])
        stat = gs.consensus

        assert stat.mean == 22.5
        assert stat.median == 22.5
