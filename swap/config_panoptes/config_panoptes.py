import datetime
import numpy as np
import numbers


# Database config options
class database:
    name = 'swapDB_panoptesTest'
    host = 'localhost'
    port = 27017
    max_batch_size = 1e5

    class panoptes_builder:

        class shared :
            upload_chunk_size = 100000

            def NanToNone(self, datum) :
                if ((isinstance(datum, numbers.Number) and np.isnan(datum)) or (isinstance(datum, str) and (datum.upper() == 'NAN'))) :
                    return None
                else :
                    return datum

        class classifications(shared) :
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

            db_to_panoptes_csv_map = { key : { 'panoptes_key' : None, 'converter_func' : lambda x : self.NanToNone(x) } for key in db_schema.keys() }

            db_to_panoptes_csv_map['classification_id']['panoptes_key'] = 'classification_id'
            db_to_panoptes_csv_map['user_id']['panoptes_key'] = 'user_id'
            db_to_panoptes_csv_map['workflow']['panoptes_key'] = 'workflow_id'
            db_to_panoptes_csv_map['time_stamp']['panoptes_key'] = 'created_at'
            db_to_panoptes_csv_map['session_id']['panoptes_key'] = 'metadata.session'
            db_to_panoptes_csv_map['live_project']['panoptes_key'] = 'metadata.live_project'
            db_to_panoptes_csv_map['seen_before']['panoptes_key'] = 'metadata.seen_before'
            db_to_panoptes_csv_map['annotation']['panoptes_key'] = 'annotations.0.value'
            db_to_panoptes_csv_map['subject_id']['panoptes_key'] = 'subject_ids'

            def convertTimeString(string) :
                # PATTERNS LIKE: 2016-08-22 16:09:01 UTC
                return datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%S %Z')

            def parseAnnotationString(string) :
                if not isinstance(string, str) :
                    print('Non-string type: {}'.format(string))
                    return False
                return True if string.startswith('Yes') else False

            db_to_panoptes_csv_map['time_stamp']['converter_func'] = convertTimeString
            db_to_panoptes_csv_map['annotation']['converter_func'] = parseAnnotationString

            skip_unpack_columns = ['subject_data']

        class subjects(shared) :

            db_schema = {
                'subject': {'type': int},
                'gold': {'type': int},
            }

            db_to_panoptes_csv_map = { key : { 'panoptes_key' : None, 'converter_func' : lambda x, *argv : self.NanToNone(x) } for key in db_schema.keys() }

            db_to_panoptes_csv_map['subject']['panoptes_key'] = 'subject_id'
            db_to_panoptes_csv_map['gold']['panoptes_key'] = 'subject_id'

            def getGoldLabelState(subject, *argv) :
                (gold_label_true_subjects, gold_label_false_subjects) = argv
                if subject in gold_label_true_subjects :
                    return 1
                elif subject in gold_label_false_subjects :
                    return 0
                else :
                    return -1

            db_to_panoptes_csv_map['gold']['converter_func'] = getGoldLabelState

            skip_unpack_columns = ['metadata']


def override(config) :
    # Database configuration
    config.database.name = database.name
    config.database.host = database.host
    config.database.port = database.port

    return None
