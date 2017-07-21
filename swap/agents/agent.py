################################################################
# Parent class for all agents

import swap.agents.ledger as ledger
from swap.utils.stats import Stat

import abc

import logging
logger = logging.getLogger(__name__)


class Agent(metaclass=abc.ABCMeta):
    """ Agent to represent a classifier (user,machine) or a subject

    Parameters:
        id: str
            Identifier of Agent
        probability: num
            Initial probability used depending on subclass.
    """

    def __init__(self, id_, ledger_type):
        self._id = id_
        self.ledger = ledger_type(id_)

    @property
    def id(self):
        return self._id

    @property
    def score(self):
        """
            Score getter function
        """
        try:
            return self.ledger.score
        except ledger.StaleException:
            return self.ledger._score

    @abc.abstractmethod
    def classify(self, cl):
        pass

    @staticmethod
    def stats(bureau):
        """
            Calculate the mean, standard deviation, and median
            of the scores in a bureau containing Agents
        """
        p = [agent.score for agent in bureau]
        return Stat(p)

    def __str__(self):
        return 'id %s transactions %d' % \
            (str(self.id), len(self.ledger.transactions))

    def __repr__(self):
        return '%s agent id %s transactions %d' % \
            (type(self), str(self.id), len(self.ledger.transactions))
