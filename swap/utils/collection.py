

class Collection:

    def __init__(self, items=None):
        if items is None:
            items = {}
        if type(items) is list:
            items = {item.id: item for item in items}
        self.items = items

    def add(self, item):
        self.items[item.id] = item

    def subset(self, items):
        subset = [self.items[i] for i in items]
        return self.__class__(subset)

    def iter(self):
        for i in self.items:
            yield self.items[i]

    def list(self):
        return list(self.items.values())

    def keys(self):
        return list(self.items.keys())

    @staticmethod
    def new(item):
        pass

    def __getitem__(self, item):
        if item not in self.items:
            self.items[item] = self.new(item)
        return self.items[item]

    def dump(self):
        data = []
        for item in self.items.values():
            data.append(item.dump())

        return data

    def truncate(self):
        for item in self.iter():
            item.truncate()

    @classmethod
    def load(cls, data):
        items = cls()
        for item in data:
            item = cls._load_item(item)
            items.items[item.id] = item
        return items

    @classmethod
    def _load_item(cls, data):
        pass

    def __str__(self):
        return '%d items' % len(self.items)

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self.items)
