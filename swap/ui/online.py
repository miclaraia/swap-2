

import click
import code

from swap.ui import ui
from swap.utils.control import SWAP
from swap.utils.online import Online


import caesar_external as ce


import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


@ui.cli.group()
def online():
    pass


@online.command
@click.argument('name')
@click.argument('online-name')
def config(name, online_name):
    swap = SWAP.load(name)
    config = swap.config
    config.online_name = online_name
    code.interact(local={**globals(), **locals()})
    swap.save()


@online.command()
@click.argument('name')
def run(name):
    swap = SWAP.load(name)
    ce.Config.load(swap.config.online_name)

    Online.receive(swap)
    swap.save()
    ce.Config.instance().save()
    logger.debug('Saved swap status')
    logger.info('Sending reductions to caesar')
    Online.send(swap)

    logger.debug('Done sending reductions to caesar')
    code.interact(local={**globals(), **locals()})


@online.command()
@click.argument('name')
def send(name):
    swap = SWAP.load(name)
    ce.Config.load(swap.config.online_name)
    logger.info('Sending reductions to caesar')
    Online.send(swap)

    logger.debug('Done sending reductions to caesar')
    code.interact(local={**globals(), **locals()})
