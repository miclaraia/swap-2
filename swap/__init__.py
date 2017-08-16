#!/usr/bin/env python

import swap.config.logger as logger
from swap.control import Control
from swap.swap import SWAP

from os import path

def version():
    root = path.dirname(__file__)
    root = path.abspath(path.join(root, '..'))

    with open(path.join(root, 'VERSION'), 'r') as f:
        version = f.readline()
        return version.strip()

__version__ = version()

assert Control
assert SWAP
assert logger
