
import pytest

from swap.utils.user import User
from swap.utils.subject import Subject
from swap.utils.config import Config


@pytest.fixture
def user():
    return User.new(123, 'name')


@pytest.fixture
def subject():
    return Subject.new(456, 1)


class TestUser:

    @staticmethod
    def test_init():
        u = User(123, 'name', ([1, 2], [3, 4]))

        assert u.id == 123
        assert u.name == 'name'
        assert u.history == []
        assert u.prior == ([1, 2], [3, 4])
        assert u.numer == [1, 2]
        assert u.denom == [3, 4]

    @staticmethod
    def test_classify(user, subject):
        user.classify(subject, 1)

        assert user.history == [(456, 1, 1)]

    @staticmethod
    def test_update_subject(user, subject):
        user.classify(subject, 1)
        user.history = [(0,), (0,)] + user.history
        subject.gold = 0
        user.update_subject(subject)

        assert user.history == [(0,), (0,), (456, 0, 1)]

    @staticmethod
    def test_update_score(user):
        user.history = [(0, 1, 1), (1, 1, 1), (2, 0, 1), (3, 0, 0)]
        user.update_score()

        assert user.numer == [1, 2]
        assert user.denom == [2, 2]

    @staticmethod
    def test_score(user):
        user.history = [(0, 1, 1), (1, 1, 1), (2, 0, 1), (3, 0, 0)]
        user.update_score()
        Config.instance().gamma = 1
        assert user.score == [.5, 3/4]
