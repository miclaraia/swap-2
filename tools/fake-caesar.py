
import swap.config as config
from swap.caesar.utils.caesar_config import CaesarConfig
from swap.caesar.auth import AuthCaesar

from flask import Flask, request, jsonify, Response
import requests
from functools import wraps
import json
import re

def debug(func):
    @wraps(func)
    def wrapper(self):
        headers = request.headers
        data = request.data
        method = request.method
        path = request.path

        print('%s to %s with %s\nheaders: %s\n' %
              (method, path, data, headers))

        return func(self)
    return wrapper


class API:

    def __init__(self):
        self.app = Flask(__name__)
        self._config = {
            'extractors_config': {},
            'reducers_config': {}
        }

        self.counter = 0
        self._key = None

    @property
    def key(self):
        if self._key is None:
            config = self._config['extractors_config']
            if 'swap' in config:
                url = config['swap']['url']
                s = '(?<=%s:).*(?=@)' % 'caesar'

                key = re.search(s, url).group(0)
                self._key = key

        return self._key

    def run(self):
        url = '/workflows/%d' % config.online_swap.workflow
        self._route(url, 'getconfig', self.get_config, ['GET'])
        self._route(url, 'putconfig', self.put_config, ['PUT'])

        url_a = url + '/reducers/swap/reductions'
        print(url_a)
        self._route(url_a, 'reduce', self.do_reduce, ['PUT'])
        url_a = url + '/extractors/swap/extractions'
        self._route(url_a, 'extract', self.do_extract, ['PUT'])

        self._route('/classify', 'classify', self.do_classify, ['GET'])
        self._route('/nclassify', 'nclassify', self.do_bad_classify, ['GET'])
        self.app.run(port=3000)

    @debug
    def get_config(self):
        return jsonify(self._config)

    @debug
    def put_config(self):
        data = request.get_json()
        self._config = data
        if 'swap' in data['extractors_config']:
            self._key = None

        return jsonify(data)

    @debug
    def do_extract(self):
        return Response(status=204)

    @debug
    def do_reduce(self):
        return Response(status=204)

    def get_swap_url(self):
        key = self.key
        if key is None:
            raise RuntimeError()

        url = 'http://caesar:%s@localhost:5000/classify' % key
        print(url)
        return url

    def classification(self, annotation):
        task = config.parser.annotation.task
        workflow = config.online_swap.workflow
        data = {
            'id': self.counter,
            'user_id': 1, 'subject_id': 1,
            'metadata': {
                'session': 1,
                'seen_before': False,
                'live_project': True,
            },
            'annotations': {task: [{'task': task, 'value': annotation}]},
            'workflow': workflow,
            'created_at': '2017-06-22T11:29:50.609Z',
        }
        self.counter += 1

        return data

    def do_classify(self):
        print('classify')
        url = self.get_swap_url()
        data = self.classification('Yes')

        requests.post(url, json=data)
        return Response(status=204)

    def do_bad_classify(self):
        print('bad-classify')
        url = self.get_swap_url()
        data = self.classification('none')

        requests.post(url, json=data)
        return Response(status=204)

    def _route(self, route, name, func, methods=('GET')):
        self.app.add_url_rule(
            route, name, func, methods=methods)


def main():
    API().run()

if __name__ == '__main__':
    main()
