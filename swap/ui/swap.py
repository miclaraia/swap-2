

import click
import csv
import code
import sys

from swap.ui import ui
from swap.utils.control import SWAP, Thresholds
from swap.utils.config import Config
from swap.utils.parser import ClassificationParser
import swap.data

import logging
logger = logging.getLogger(__name__)


@ui.cli.command()
@click.argument('name')
@click.option('--all', is_flag=True)
def clear(name, all):
    swap.data.clear(name, all)


@ui.cli.command()
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

            # if i > 0 and i % 1e6 == 0:
                # print()
                # print('Applying records')
                # swap()
                # swap.truncate()

    swap()
    swap.retire()
    swap.save()

    code.interact(local={**globals(), **locals()})


@ui.cli.command()
@click.argument('name')
@click.option('--config', is_flag=True)
def new(name, config):
    _c = config
    config = Config(name)
    if _c:
        code.interact(local=locals())
    swap = SWAP(config)
    print(config)
    swap.save()


@ui.cli.command()
@click.argument('name')
def load(name):
    swap = SWAP.load(name)
    code.interact(local={**globals(), **locals()})

@ui.cli.command()
def list():
    for row, config in swap.data.list_config():
        print('%s: %s' % (row, config))


@ui.cli.command()
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
