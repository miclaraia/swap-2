from tools.panoptes.csv_dump_parser import CsvDumpParser
from swap.config_panoptes import panoptes_database

import swap.db
import swap.config_panoptes as config

import os
import sys
import argparse

import logging
logger = logging.getLogger(__name__)

# DB SCHEMA
# {
#     'classification_id': 15935073,
#     'user_id': 1460166,
#     'workflow': 2473,
#     'time_stamp': datetime.datetime(2016, 8, 22, 16, 10, 26),
#     'session_id': '6049552d100cae2a9570c40bee1119cfbca4decae1e50bafffc3cba873793d6f',
#     'live_project': False,
#     'seen_before': False,
#     'annotation': 1,
#     'subject_id': 3354054,
# }


def main() :
    db = swap.db.DB()

    argParser = argparse.ArgumentParser(prefix_chars='-')
    argParser.add_argument('panoptesdumpfile')
    argParser.add_argument('--record-range', nargs=2, type=int, default=[0, -1], metavar=('first', 'last'))
    argParser.add_argument('--dryrun', nargs='?', type=bool, default=False)
    argParser.add_argument('--true_gold_subjects',
                           help='Path to file containing a newline-separated list of true-label gold standard subjects',
                           nargs='?', type=str, default='')
    argParser.add_argument('--false_gold_subjects',
                           help='Path to file containing a newline-separated list of false-label gold standard subjects',
                           nargs='?', type=str, default='')
    args = argParser.parse_args()
    print("Using file %s" % args.panoptesdumpfile)

    if not os.path.isfile(args.panoptesdumpfile):
        raise FileNotFoundError("Couldn't find file at '%s'" % args.panoptesdumpfile)
    if args.panoptesdumpfile.split('.')[-1] != 'csv':
        raise ValueError("File '%s' not a valid csv file" % args.panoptesdumpfile)

    trueGoldSubjects = [] if args.true_gold_subjects == '' else loadSubjectList(args.true_gold_subjects)
    falseGoldSubjects = [] if args.false_gold_subjects == '' else loadSubjectList(args.false_gold_subjects)

    print('{}: trueGoldSubjects\n{}'.format(__file__, repr(trueGoldSubjects)))

    csvParser = CsvDumpParser(args.panoptesdumpfile)

    if not args.dryrun :
        logger.info('Dropping subjects collection.')
        db._db.subjects.drop()

    for startRow in range(args.record_range[0], args.record_range[1], config.panoptes_database.panoptes_builder.subjects.upload_chunk_size) :

        rowRange = (startRow, startRow + config.panoptes_database.panoptes_builder.subjects.upload_chunk_size)

        flattenedData = csvParser.getUnpackedData(skipUpackingFor = config.panoptes_database.panoptes_builder.subjects.skip_unpack_columns, rowRange = rowRange)

        dataForUpload = []
        for _, data in flattenedData.iterrows() :
            datumForUpload = {}
            for dbKey, mappings in config.panoptes_database.panoptes_builder.subjects.db_to_panoptes_csv_map.items() :
                datumForUpload.update({dbKey : mappings['converter_func'](data.loc[mappings['panoptes_key']], trueGoldSubjects, falseGoldSubjects) if mappings['panoptes_key'] in data else None})
            dataForUpload.append(datumForUpload)
        upload(dataForUpload, args)
        csvParser.reset()


def upload(dataForUpload, args):
    db = swap.db.DB()
    numRecords = len(dataForUpload)
    if numRecords > 0 :
        logger.info('Uploading {} records'.format(numRecords))
        if not args.dryrun :
            logger.info('Writing to DB...')
            db.subjects.insert_many(dataForUpload)
            db._gen_stats()
        else :
            logger.info('Running with --dryrun. DB will not be modified.')
        logger.info('Done.')


def loadSubjectList(listFilePath) :
    if os.path.exists(listFilePath) :
        with open(listFilePath) as listFile :
            return [int(line) for line in listFile if '#' not in line]
    else :
        logger.warn('Could not find {}, returning zero length list.'.format(listFilePath))
        return []

if __name__ == '__main__' :
    main()
