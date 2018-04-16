#!/usr/bin/env python

from os import path


def version():
    root = path.dirname(__file__)
    root = path.abspath(path.join(root, '..'))

    with open(path.join(root, 'VERSION'), 'r') as f:
        v = f.readline()
        return v.strip()

__version__ = version()