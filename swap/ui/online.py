

import click
import code

from swap.ui import ui
from swap.utils.control import SWAP
from swap.utils.online import Online


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

    Online.receive(swap)
    Online.send(swap)
    swap.save()

    code.interact(local={**globals(), **locals()})
    ce.Config.instance().save()
