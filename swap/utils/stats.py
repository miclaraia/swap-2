
import statistics as st


class BaseStat:
    pass


class Stat(BaseStat):
    """
        Keeps track of statistics in a dataset
    """

    def __init__(self, data):
        self.mean = st.mean(data)
        self.median = st.median(data)
        self.stdev = st.pstdev(data)

    def dict(self):
        return {'mean': self.mean,
                'stdev': self.stdev,
                'median': self.median}

    def __str__(self):
        return 'mean: %.4f median %.4f stdev %.4f' % \
            (self.mean, self.median, self.stdev)


class MultiStat(BaseStat):
    """
        Keeps track of statistics for multiple classes in a single
        category. For example, the 0 and 1 scores of each user agent.
    """

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

    def dict(self):
        export = {}
        for label, stat in self.stats.items():
            export[label] = stat.dict()

        return export

    def __str__(self):
        s = ''
        for label, stat in self.stats.items():
            s += 'stat %s %s\n' % (str(label), str(stat))
        return s


class Stats:
    """
        A collection of multiple BaseStat objects
    """

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

    def dict(self):
        export = {}
        for name, stat in self.stats.items():
            export[name] = stat.dict()

    def __str__(self):
        s = ''
        stats = sorted(self.stats.items(), key=lambda item: item[0])
        for name, stat in stats:
            name = str(name)
            s += '%s\n' % name
            s += ''.join(['-' for c in name])
            s += '\n'
            s += '%s\n' % str(stat)
        return s
