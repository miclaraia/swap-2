import datetime


# Database config options
class database:
    name = 'swapDB'
    host = 'localhost'
    port = 27017
    max_batch_size = 1e5

    class builder:

        # SCHEMA FIELDS
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

        db_schema = {
            'classification_id': {'type': int},
            'user_id': {'type': int},
            'workflow': {'type': int},
            'time_stamp': {'type': type(datetime.datetime)},
            'session_id': {'type': int},
            'live_project': {'type': bool},
            'seen_before': {'type': bool},
            'annotation': {'type': bool},
            'subject_id': {'type': int},
        }

        db_to_panoptes_csv_map = { {key : { 'panoptes_key' : None, 'converter_func' : lambda x : x } } }

        db_to_panoptes_csv_map['classification_id']['panoptes_key'] = 'classification_id'
        db_to_panoptes_csv_map['user_id']['panoptes_key'] = 'user_id'
        db_to_panoptes_csv_map['workflow']['panoptes_key'] = 'workflow_id'
        db_to_panoptes_csv_map['time_stamp']['panoptes_key'] = 'created_at'
        db_to_panoptes_csv_map['session_id']['panoptes_key'] = 'metadata.session'
        db_to_panoptes_csv_map['live_project']['panoptes_key'] = 'metadata.live_project'
        db_to_panoptes_csv_map['seen_before']['panoptes_key'] = 'metadata.seen_before'
        db_to_panoptes_csv_map['annotation']['panoptes_key'] = 'annotations.zero.value'
        db_to_panoptes_csv_map['subject_id']['panoptes_key'] = 'subject_ids'

        def convertTimeString(string) :
            return datetime.strptime(string, '%Y-%m-%dT%H:%M:%S')

        def parseAnnotationString(string) :
            return True if string.startswith('Yes') else False

        db_to_panoptes_csv_map['time_stamp']['converter_func'] = convertTimeString
        db_to_panoptes_csv_map['annotation']['converter_func'] = parseAnnotationString
