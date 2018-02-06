

import click
import csv
import code
import sys

from swap.ui import ui
from swap.utils.control import SWAP, Config, Thresholds
from swap.utils.parser import AnnotationParser

import caesar_external as ce


import logging
logger = logging.getLogger(__name__)


@ui.cli.group()
def online():
    pass


@online.command()
@click.argument('name')
@click.option('--online-name')
def run(name, online_name):
    if not online_name:
        online_name = name
    ce.Config.load(online_name)
    swap = SWAP.load(name)
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
    swap.save()

    code.interact(local={**globals(), **locals()})
    ce.Config.instance().save()


