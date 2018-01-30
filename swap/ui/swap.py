

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
def clear(name):
    swap = SWAP.load(name)
    swap = SWAP(name, swap.config)
    swap.save()

@swap.command()
@click.argument('name')
@click.argument('data')
def run(name, data):
    swap = SWAP.load(name)
    config = swap.config
    parser = ClassificationParser(config)

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

            if i > 0 and i % 1e6 == 0:
                print()
                print('Applying records')
                swap()
                swap.truncate()

    swap()
    swap.retire(config.fpr, config.mdr)
    swap.save()

    code.interact(local={**globals(), **locals()})


@swap.command()
@click.argument('name')
@click.option('--config', is_flag=True)
def new(name, config):
    if config:
        config = Config()
        code.interact(local=locals())
        swap = SWAP(name, config)
    else:
        swap = SWAP(name)
    swap.save()

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
