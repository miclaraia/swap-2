from tools.panoptes.csv_dump_parser import CsvDumpParser
from swap.config_panoptes import panoptes_database

import swap.db
import swap.config_panoptes as config

import os
import sys
import argparse

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
    argParser.add_argument('panoptes-dumpfile', dest='file')
    argParser.add_argument('--limit-records', nargs='?', const=1, type=int, default=-1)
    argParser.add_argument('--dryrun', nargs='?', const=True, type=bool, default=False)
    args = argParser.parse_args()
    print("Using file %s" % args.file)

    if not os.path.isfile(args.file):
        raise FileNotFoundError("Couldn't find file at '%s'" % args.file)
    if args.file.split('.')[-1] != 'csv':
        raise ValueError("File '%s' not a valid csv file" % args.file)

    csvParser = CsvDumpParser(file)
    flattenedData = csvParser.getUnpackedData(skipUpackingFor = config.database.panoptes_builder.skip_unpack_columns, rowRange = (0, args.limit_records))

    dataForUpload = []
    for _, data in flattenedData.iterrows() :
        datumForUpload = {}
        for dbKey, mappings in config.database.panoptes_builder.db_to_panoptes_csv_map.items() :
            datumForUpload.update({dbKey : mappings['converter_func'](data.loc['panoptes_key']) if mappings['panoptes_key'] in data else None})
        dataForUpload.append(datumForUpload)

    upload(dataForUpload)


def upload(dataForUpload):
    print(dataForUpload)
    if not dryrun :
        db = swap.db.DB()
        db.classifications.insert_many(dataForUpload)


if __name__ == '__main__' :
    main()
