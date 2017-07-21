
from swap.db.db import Collection
import swap.utils.parsers as parsers
import swap.config as config

import sys
import csv
import logging
logger = logging.getLogger(__name__)


class Subjects(Collection):

    @staticmethod
    def _collection_name():
        return 'subjects'

    @staticmethod
    def _schema():
        return config.parser.subject_metadata

    def _init_collection(self):
        pass

    #######################################################################

    def get_metadata(self, subject_id):
        cursor = self.collection.find({'subject': subject_id}).sort('_id', -1)

        try:
            data = cursor.next()
            data.pop('_id')
            return data
        except StopIteration:
            pass

    def upload_metadata_dump(self, fname):
        self._rebuild()

        logger.info('parsing csv dump')
        data = []
        parser = parsers.MetadataParser('csv')

        with open(fname, 'r') as file:
            reader = csv.DictReader(file)

            for i, row in enumerate(reader):
                item = parser.process(row)
                print(item)
                data.append(item)

                sys.stdout.flush()
                sys.stdout.write("%d records processed\r" % i)

                if len(data) > 100000:
                    print(data)
                    self.collection.insert_many(data)
                    data = []

        self.collection.insert_many(data)
        logger.debug('done')


class SubjectStats:

    def __init__(self, subject_id, db):
        self.id = subject_id
        self.annotations = self._annotations(db, subject_id)

    def dict(self):
        return {
            'subject_id': self.id,
            'annotations': self.annotations,
            'controversial': self.controversial,
            'consensus': self.consensus
        }

    @staticmethod
    def _annotations(db, subject_id):
        query = [
            {'$match': {'seen_before': False, 'subject_id': subject_id}},
            {'$project': {'annotation': 1}}
        ]
        cursor = db.classifications.aggregate(query)

        counts = {0: 0, 1: 0}
        for cl in cursor:
            counts[cl['annotation']] += 1

        return counts

    @property
    def controversial(self):
        yes = self.annotations[1]
        no = self.annotations[0]
        a = min(yes, no)
        b = max(yes, no)

        return (a + b) ** (a / b)

    @property
    def consensus(self):
        yes = self.annotations[1]
        no = self.annotations[0]
        a = min(yes, no)
        b = max(yes, no)

        return (b - a) ** (1 - a / b)

    def print_(self):
        print(self)

    def __str__(self):
        return \
            'subject %(subject_id)9d ' \
            'controversial %(controversial)8.4f ' \
            'consensus %(consensus)8.4f ' \
            'annotations %(annotations)s' \
            % self.dict()

    def __repr__(self):
        return str(self.dict())
