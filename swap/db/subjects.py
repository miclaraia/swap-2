
from swap.db.db import Collection
import swap.utils.parsers as parsers
import swap.config as config

import sys
import csv
from pymongo import IndexModel, ASCENDING
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
        indexes = [
            IndexModel([('subject', ASCENDING)])
        ]

        logger.debug('inserting %d indexes', len(indexes))
        self.collection.create_indexes(indexes)
        logger.debug('done')

    #######################################################################

    def get_metadata(self, subject_id):
        cursor = self.collection.find({'subject': subject_id}).sort('_id', -1)

        try:
            data = cursor.next()
            data.pop('_id')
            return data
        except StopIteration:
            pass

    def get_subjects(self):
        cursor = self.collection.find(projection={'subject': 1})
        subjects = []

        for item in cursor:
            subjects.append(item['subject'])

        return subjects

    def get_stats(self, subject_id):
        cursor = self.collection.find({'subject': subject_id})

        if cursor.count() > 0:
            item = cursor.next()['stats']
            cursor.close()
            return item
        cursor.close()

    def calculate_subject_stats(self):
        subjects = self._db.classifications.get_subjects()

        logger.info('Updating subject stats')
        count = 0
        for subject in subjects:
            id_ = subject['_id']
            stats = SubjectStats.new(id_, self._db)
            data = stats.dict()
            data.pop('subject_id')

            self.collection.update_one(
                {'subject': id_}, {'$set': {'stats': data}}, upsert=True)

            count += 1
            if count % 100 == 0:
                sys.stdout.flush()
                sys.stdout.write("Updated %d subjects\r" % count)
        print()

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

    def __init__(self, subject_id, annotations, controversial, consensus):
        self.id = subject_id
        self.annotations = annotations

        self.controversial = controversial
        self.consensus = consensus

    @classmethod
    def new(cls, subject_id, db):
        annotations = cls._annotations(db, subject_id)

        controversial = cls._controversial(annotations)
        consensus = cls._consensus(annotations)

        return cls(subject_id, annotations, controversial, consensus)

    @classmethod
    def from_static(cls, subject_id, db):
        stats = db.subjects.get_stats(subject_id)

        annotations = stats.pop('annotations')
        annotations = {0: annotations['N'], 1: annotations['Y']}

        return cls(subject_id, annotations, **stats)

    def dict(self):
        annotations = {'N': self.annotations[0], 'Y': self.annotations[1]}
        return {
            'subject_id': self.id,
            'annotations': annotations,
            'controversial': self.controversial,
            'consensus': self.consensus
        }

    @staticmethod
    def _annotations(db, subject_id):
        query = [
            {'$match': {'seen_before': False, 'subject_id': subject_id}},
            {'$project': {'annotation': 1}}
        ]
        cursor = db.classifications.aggregate(query, debug_query=False)

        counts = {0: 0, 1: 0}
        for cl in cursor:
            counts[cl['annotation']] += 1

        return counts

    @staticmethod
    def _controversial(annotations):
        yes = annotations[1]
        no = annotations[0]
        a = min(yes, no)
        b = max(yes, no)

        return (a + b) ** (a / b)

    @staticmethod
    def _consensus(annotations):
        yes = annotations[1]
        no = annotations[0]
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
