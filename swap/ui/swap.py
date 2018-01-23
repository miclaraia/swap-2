

import click
import csv
import code

from swap.ui import ui
from swap.utils.control import SWAP, Config
from swap.utils.parser import ClassificationParser


@ui.cli.group()
def swap():
    pass

@swap.command()
@click.argument('name')
@click.argument('data')
def test(name, data):
    annotation = {
        'task': 'T1',
        'true': ['Yes!', 1],
        'false': ['No.', 0],
    }
    config = Config(annotation=annotation)
    parser = ClassificationParser(config)
    swap = SWAP(name)

    with open(data, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            print(row)
            swap.classify(**parser.parse(row))

    print('score users')
    swap.score_users()
    print('apply subjects')
    swap.apply_subjects()
    print('score_subjects')
    swap.score_subjects()

    code.interact(local={**globals(), **locals()})


@swap.command()
@click.argument('name')
def load(name):
    swap = SWAP.load(name)
    code.interact(local={**globals(), **locals()})



    

