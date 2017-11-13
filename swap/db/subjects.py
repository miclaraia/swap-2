
from swap.db.db import Collection
import swap.utils.parsers as parsers
import swap.config as config
import swap.utils.scores

import sys
import csv
from pymongo import IndexModel, ASCENDING, UpdateOne
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

        logger.info('Updating %d subject stats', len(subjects))
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


    #######################################################################
    #####   Metadata   ####################################################
    #######################################################################

    def get_metadata(self, subject_id):
        cursor = self.collection.find({'subject': subject_id}).sort('_id', -1)

        try:
            data = cursor.next()
            return data['metadata']
        except StopIteration:
            pass

    def update_metadata(self, subject, metadata, write=True):
        updates = {}
        for key, value in metadata.items():
            updates['metadata.%s' % key] = value
        request = {
            'filter': {'subject': subject},
            'update': {'$set': updates},
        }

        if write:
            self.collection.update_one(**request)
        else:
            return UpdateOne(**request)

    def upload_metadata_dump(self, fname):
        logger.info('parsing csv metadata')
        parser = parsers.MetadataParser('csv')

        with open(fname, 'r') as file:
            reader = csv.DictReader(file)
            requests = []

            for i, row in enumerate(reader):
                subject, metadata = parser.process(row)
                requests.append(self.update_metadata(subject, metadata, False))

                if i % 100 == 0:
                    sys.stdout.flush()
                    sys.stdout.write("%d records processed\r" % i)

                if len(requests) > 100000:
                    print('uploading requests')
                    self.collection.bulk_write(requests)
                    requests = []

        self.collection.bulk_write(requests)
        logger.debug('done')

    #######################################################################
    #####   ###############################################################
    #######################################################################

    def save_scores(self, scores):
        requests = []
        for score in scores:
            requests.append(UpdateOne(
                {'subject': score.id},
                {'$set': {'score': score.p, 'retired_as': score.label}}
            ))

        self.collection.bulk_write(requests)

    def get_scores(self):
        Score = swap.utils.scores.Score
        ScoreExport = swap.utils.scores.ScoreExport

        cursor = self.collection.find(
            {},
            {'subject': 1, 'gold': 1, 'score': 1, 'retired_as': 1}
        )

        scores = {}
        for item in cursor:
            s = item['subject']
            g = item.get('gold', -1)
            p = item['score']
            label = item['retired_as']
            score = Score(s, g, p)
            score.label = label

            scores[s] = score

        se = ScoreExport(scores, False)
        se.gold_getter = None
        return se


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
        annotations = {
            'N': self.annotations[0],
            'Y': self.annotations[1],
            'total': sum([self.annotations[i] for i in [0, 1]])
        }

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

        return (a + b) ** (a / b - 1)

    @staticmethod
    def _consensus(annotations):
        yes = annotations[1]
        no = annotations[0]
        a = min(yes, no)
        b = max(yes, no)

        return (a + b) ** (- a / b)

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
