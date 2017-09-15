README
======

Documentation
-------------

Full documentation is available [here](https://zooniverse.github.io/swap/)

Quick Start
-----------

Install SWAP

`./bin/install`

Run Online SWAP

`./bin/run_online_swap`


Using SWAP
----------

After installing, there are a number of commands available for running SWAP.
These include tools to create plots and export SWAP scores to file.

Basic syntax is

    run_swap [options] COMMAND [options]

Command can be one of `{roc, swap}`

To run swap and pickle and save, run

    run_swap swap --run 

Find more details by running

    run_swap -h

or, for more details about SWAP specific commands, run

    run_swap swap -h
