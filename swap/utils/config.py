

class Config:

    _instance = None

    def __init__(self, **kwargs):
        annotation = {
            'task': 'T1',
            'value_key': None,
            'value_separator': '.',
            'true': [1],
            'false': [0],
        }
        if 'annotation' in kwargs:
            annotation.update(kwargs['annotation'])
        self.annotation = annotation
        self.mdr = kwargs.get('mdr', .1)
        self.fpr = kwargs.get('fpr', .01)

        self.gamma = kwargs.get('gamma', 1)
        self.p0 = kwargs.get('p0', .12)
        self.user_default = kwargs.get('user_default', [.5, .5])

        self.online_name = kwargs.get('online_name', None)

        self.__class__._instance = self

    @classmethod
    def instance(cls):
        if isinstance(cls._instance, cls):
            return cls._instance
        return cls()

    def dump(self):
        return self.__dict__.copy()

    @classmethod
    def load(cls, dump):
        config = cls()
        config.__dict__.update(dump)
        return config

    def __str__(self):
        return str(self.dump())

    def __repr__(self):
        return str(self)
