
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
        for subject in swap.subjects.iter():
            data.append((subject.id, {'score': subject.score}))

        ce.Reducer.reduce(data)

    @staticmethod
    def receive(swap):
        config = swap.config
        parser = AnnotationParser(config)

        data = ce.Extractor.next()
        for i, item in enumerate(data):
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

            swap.classify(**cl)

        swap()
        swap.retire(config.fpr, config.mdr)
        return swap
