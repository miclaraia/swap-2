
from swap.utils.parser import AnnotationParser
try:
    import caesar_external as ce
except ModuleNotFoundError:
    pass
import sys
import logging

logger = logging.getLogger(__name__)


class Online:

    @staticmethod
    def send(swap):
        logger.debug('Sending data')
        data = []
        subjects = swap.subjects.get_changed()
        for subject in subjects.iter():
            data.append((subject.id, {'score': subject.score}))

        ce.Reducer.reduce(data)
        for subject in subjects.iter():
            subject.has_changed = False

    @staticmethod
    def receive(swap):
        config = swap.config
        parser = AnnotationParser(config)

        data = ce.Extractor.next()
        haveItems = False
        for i, item in enumerate(data):
            logger.debug('Received annotation: Type ({}): {}'.format(type(item['annotations']), item['annotations']))
            haveItems = True
            cl = {
                'user': item['user'],
                'subject': item['subject'],
                'cl': parser.parse(item['annotations']),
                'id_': item['id']
            }
            if cl['cl'] is None:
                continue

            if i % 100 == 0:
                sys.stdout.flush()
                sys.stdout.write("%d records processed\r" % i)

            logger.debug('Received classification: {}'.format(cl))

            swap.classify(**cl)

        if haveItems:
            swap()
            swap.retire()
        return swap, haveItems
