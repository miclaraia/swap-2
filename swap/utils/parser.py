
import json


class ClassificationParser:

    def __init__(self, config):
        self.annotation = AnnotationParser(config)

    def parse(self, cl):
        user = cl['user_id']
        if user == '':
            user = 0
        else:
            user = int(user)
        return {
            'user': user,
            'subject': int(cl['subject_ids']),
            'cl': int(self.annotation.parse(cl))
        }


class AnnotationParser:

    def __init__(self, config):
        self.parser = config.annotation

    def parse(self, cl):
        annotations = json.loads(cl['annotations'])
        annotation = self._find_task(annotations)

        value = self._parse_value(annotation['value'])
        if value is None:
            task = self.parser['task']
            value_key = self.parser['value_key']
            print(task, value_key)
            raise Exception

        return value

    @staticmethod
    def _navigate(obj, dotkey, split='.'):
        steps = dotkey.split(split)
        item = obj

        for key in steps:
            if type(item) is list:
                key = int(key)

            item = item[key]

        return item

    def _find_task(self, annotations):
        """
        Find the right task from the annotation field in a classification

        Needs to be dynamic because csv dump and caesar stream send
        classifications with different formats
        """
        task = self.parser['task']
        if type(annotations) is dict and task in annotations:
            return annotations[task][0]

        if type(annotations) is list:
            for annotation in annotations:
                if annotation['task'] == task:
                    return annotation

        raise Exception
        # raise self.AnnotationError(task, '', annotations)

    def _parse_value(self, value):
        """
        Parses the value field of an annotation task
        """
        key = self.parser['value_key']
        sep = self.parser['value_separator']

        if key is not None:
            value = self._navigate(value, key, sep)

        if value in self.parser['true']:
            return 1
        if value in self.parser['false']:
            return 0
