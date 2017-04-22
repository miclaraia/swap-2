################################################################
# Parent class for all agents

import abc
import statistics as st

from swap.agents.tracker import Tracker


class Agent(metaclass=abc.ABCMeta):
    """ Agent to represent a classifier (user,machine) or a subject

    Parameters:
        id: str
            Identifier of Agent
        probability: num
            Initial probability used depending on subclass.
    """

    def __init__(self, id, probability):
        self.id = id
        self.probability = probability

        self.annotations = Tracker()

    def getID(self):
        """ Returns Agents ID """
        return self.id

    @staticmethod
    def stats(bureau):
        """
            Calculate the mean, standard deviation, and median
            of the scores in a bureau containing Agents
        """
        p = [agent.getScore() for agent in bureau]
        return Stat(p)

    @abc.abstractmethod
    def export(self):
        """
            Abstract method to export agent data
        """
        return


class BaseStat:
    pass


class Stat(BaseStat):
    def __init__(self, data):
        self.mean = st.mean(data)
        self.median = st.median(data)
        self.stdev = st.pstdev(data)

    def export(self):
        return {'mean': self.mean,
                'stdev': self.stdev,
                'median': self.median}

    def __str__(self):
        return 'mean: %.4f median %.4f stdev %.4f' % \
            (self.mean, self.median, self.stdev)


class MultiStat(BaseStat):
    def __init__(self, *data):
        stats = {}
        for label, p in data:
            stats[label] = Stat(p)
        self.stats = stats

    def add(self, label, stat):
        self.stats[label] = stat

        return self

    def addNew(self, label, data):
        self.add(label, Stat(data))

    def export(self):
        export = {}
        for label, stat in self.stats.items():
            export[label] = stat.export()

        return export

    def __str__(self):
        s = ''
        for label, stat in self.stats.items():
            s += 'stat %s %s\n' % (str(label), str(stat))
        return s


class Stats:
    def __init__(self):
        self.stats = {}

    def add(self, name, stat):
        if not isinstance(stat, BaseStat):
            raise TypeError('Stat must be of type BaseStat')
        self.stats[name] = stat

        return self

    def get(self, name):
        if name not in self.stats:
            raise KeyError('%s not a valid stat name' % name)
        return self.stats[name]

    def export(self):
        export = {}
        for name, stat in self.stats.items():
            export[name] = stat.export()

    def __str__(self):
        s = ''
        for name, stat in self.stats.items():
            name = str(name)
            s += '%s\n' % name
            s += ''.join(['-' for c in name])
            s += '\n'
            s += '%s\n' % str(stat)
        return s
