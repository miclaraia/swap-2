
import caesar_external as ce
from swap.utils.parser import AnnotationParser


class Online:

    @staticmethod
    def send(swap):
        data = []
        for subject in swap.subjects.iter():
            data.append((subject.id, {'score': subject.score}))

        ce.Reducer.reduce(data)

    @staticmethod
    def receive(swap):
        config = swap.config
        parser = AnnotationParser(config)

        data = ce.Extractor.next()
        for item in data:
            cl = {
                'user': item['user'],
                'subject': item['subject'],
                'cl': parser.parse(item['annotations']),
                'id_': item['id']
            }
            if cl['cl'] is None:
                continue

            swap.classify(**cl)

        swap()
        swap.retire(config.fpr, config.mdr)
        return swap
