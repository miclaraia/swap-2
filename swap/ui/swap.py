

import click
import csv
import code
import sys

from swap.ui import ui
from swap.utils.control import SWAP, Config, Thresholds
from swap.utils.parser import ClassificationParser

import logging
logger = logging.getLogger(__name__)


@ui.cli.group()
def swap():
    pass

@swap.command()
@click.argument('name')
@click.argument('data')
def run(name, data):
    annotation = {
        'task': 'T1',
        'true': ['Real', 'Yes', 1],
        'false': ['Bogus', 'No', 0],
    }
    config = Config(annotation=annotation)
    parser = ClassificationParser(config)
    swap = SWAP.load(name)

    with open(data, 'r') as file:
        reader = csv.DictReader(file)
        for i, row in enumerate(reader):
            row = parser.parse(row)
            if row is None:
                logger.error(row)
                continue

            if i % 100 == 0:
                sys.stdout.flush()
                sys.stdout.write("%d records processed\r" % i)

            swap.classify(**row)

    swap()
    swap.retire(config.fpr, config.mdr)
    swap.save()

    code.interact(local={**globals(), **locals()})


@swap.command()
@click.argument('name')
def load(name):
    swap = SWAP.load(name)
    code.interact(local={**globals(), **locals()})


@swap.command()
@click.argument('name')
@click.argument('path')
def golds(name, path):
    golds = []
    with open(path, 'r') as file:
        reader = csv.DictReader(file)
        for i, row in enumerate(reader):
            golds.append((int(row['subject']), int(row['gold'])))

            if i % 100 == 0:
                sys.stdout.flush()
                sys.stdout.write("%d records processed\r" % i)

    swap = SWAP.load(name)
    swap.apply_golds(golds)
    swap.save()
    code.interact(local={**globals(), **locals()})
