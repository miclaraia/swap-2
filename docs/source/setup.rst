
Getting Started
===============

Installation
------------

Automatic Installation
~~~~~~~~~~~~~~~~~~~~~~

Clone this repository::

    git clone https://github.com/miclaraia/swap.git

Run the builtin setup script::
    
    ./swap/bin/install

This script will create a virtual environment in the cloned git repository
and install swap inside. It will also copy the default swap config file
to the local location in `swap/conf/swap.conf`. SWAP will look for this config
file in the following locations, and use the first one it finds:

    #. A location specified in the :code:`SWAP_CONFIG` environment variable
    #. :code:`~/.swaprc`
    #. :code:`/etc/swap/swap.conf`
    #. :code:`swap/conf/swap.conf` in the local SWAP installation directory

SWAP depends on an external MongoDB database. Make sure you have this installed
on the system. Find it in your distribution's repositories, or build it from
source. Find more information `here <https://www.mongodb.com/>`_

Manual Installation
~~~~~~~~~~~~~~~~~~~

It is recommended to set up a virtual environment and install SWAP
and its dependencies inside. Find more information about virtual environments
`here <http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/>`_,
and information about conda `conda <https://conda.io/docs/using/>`_.

First, clone the repository::

    git clone https://github.com/miclaraia/swap.git

Create a virtual environment::

    mkvirtualenv swap --python=/usr/bin/python3 swap

Install SWAP::

    pip install -e swap

*Development Mode:* Pip can also install SWAP in development mode. This means pip will install
the project in editable mode, so changes to the source affect the runtime version.
It will also install additional dependencies for testing and development.
To do this, clone the git repository, navigate to the projectd directory, and run::

    pip install -e hco-experiments/swap[dev,test]


Configuring SWAP
----------------

SWAP has a number of config options that can be specified in the config file.
A template config file is located in :code:`swap/conf/swap.default.conf`. The
config file is a python script, and SWAP tries to call the following function in
the config to override SWAP options::

    def override(config):
        # Override config options


Caesar Integration
~~~~~~~~~~~~~~~~~~

+--------------------------------+-----------------------------------------------------------------+
| Configuration path             | Description                                                     |
+================================+=================================================================+
| config.online_swap.project     |                                                                 |
+--------------------------------+-----------------------------------------------------------------+
| config.online_swap.project     | p{90} Name of the project used in the caesar config. Make sure  |
|                                | to configure your webserver to route traffic to                 | 
|                                | :code:`$HOSTNAME/{project}`                                     |
|                                |                                                                 |
|                                |                                                                 |
|                                |                                                                 |
+--------------------------------+-----------------------------------------------------------------+
| config.online_swap.workflow    | The workflow id of this project in Panoptes.                    |
|                                |                                                                 |
+--------------------------------+-----------------------------------------------------------------+
| config.online_swap.host        | Hostname that caesar should use to send classifications to SWAP |
|                                |                                                                 |
+--------------------------------+-----------------------------------------------------------------+
| config.online_swap.ext_port    | The external port that the webserver is listening on. We        |
|                                | recommend leaving this set to 443, and configuring the          |
|                                | webserver to use SSL. SWAP currently authenticates caesar using |
|                                | using plaintext HTTP Basic Auth, so it's important that the     |
|                                | traffic is encrypted so the credentials remain private.         |
|                                |                                                                 |
|                                |                                                                 |
|                                |                                                                 |
+--------------------------------+-----------------------------------------------------------------+
| config.online_swap.port        | Port that SWAP should listen to internally.                     |
|                                |                                                                 |
+--------------------------------+-----------------------------------------------------------------+
| config.online_swap.caesar.\    | Endpoint that SWAP should use to connect to caesar. Useful to   |
| caesar_endpoint                | test things on staging before using production.                 |
|                                | Known options are :code:`caesar-staging` for staging            |
|                                | (caesar-staging.zooniverse.org) and :code:`caesar` for          |
|                                | production (caesar.zooniverse.org)                              |
|                                |                                                                 |
+--------------------------------+-----------------------------------------------------------------+
| config.online_swap.caesar.\    | Endpoint that SWAP should use to connect to Panoptes. Useful to |
| panoptes_endpoint              | test things on staging before using production.                 |
|                                | Known options are :code:`panoptes-staging` for staging          |
|                                | (panoptes-staging.zooniverse.org) and :code:`panoptes` for      |
|                                | production (panoptes.zooniverse.org)                            |
|                                |                                                                 |
+--------------------------------+-----------------------------------------------------------------+


Parsing Classifications
~~~~~~~~~~~~~~~~~~~~~~~

Use these configuration options to set how SWAP parses classification. SWAP uses
these options both to parsing from the panoptes classification dump, and to
parse incoming classifications from Caesar.

+--------------------------------+-----------------------------------------------------------------+
| Configuration path             | Description                                                     |
+================================+=================================================================+
| config.parser.annotation.task  | Task identifier. Usually :code:`T0` or :code:`T1`. You can find |
|                                | this by looking at the :code:`annotation` column in the         |
|                                | classification dump csv                                         |
|                                |                                                                 |
+--------------------------------+-----------------------------------------------------------------+
| config.parser.annotation.\     | Name of the value field. If this is nested in the task, use a   |
| value_key                      | :code:`.` to separate the identifier for each level.            |
|                                |                                                                 |
+--------------------------------+-----------------------------------------------------------------+
| config.parser.annotation.true  | Array of values that have been used in the project to identify  |
|                                | a :code:`true` classification. This field *MUST* be a list,     |
|                                | and the list *MUST* include a :code:`1` because of how Caesar   |
|                                | sends the classification data.                                  |
|                                |                                                                 |
+--------------------------------+-----------------------------------------------------------------+
| config.parser.annotation.false | Array of values that have been used in the project to identify  |
|                                | a :code:`false` classification. This field *MUST* be a list,    |
|                                | and the list *MUST* include a :code:`0` because of how Caesar   |
|                                | sends the classification data.                                  |
|                                |                                                                 |
+--------------------------------+-----------------------------------------------------------------+


Logging
~~~~~~~

+--------------------------------+-----------------------------------------------------------------+
| Configuration path             | Description                                                     |
+================================+=================================================================+
| config.logging.files.version   | :code:`dyanmic`: Each concurrent SWAP instance writes to its    |
|                                | own log file. The PID of the calling shell is appended to the   |
|                                | log filemame.                                                   |
|                                |                                                                 |
|                                | :code:`static`: log messages are all sent to the same file      |
|                                |                                                                 |
+--------------------------------+-----------------------------------------------------------------+
| config.logging.files.static    | Filename to use if :code:`config.logging.files.version` is set  |
|                                | set to :code:`static`                                           |
|                                |                                                                 |
+--------------------------------+-----------------------------------------------------------------+
| config.logging.files.\         | Maximum file size of a log file in MB. SWAP rotates log files   |
| max_size_mb                    | when the file reaches this size.                                |
|                                |                                                                 |
+--------------------------------+-----------------------------------------------------------------+
| config.logging.files.\         | Number of log files to keep after rotating                      |
| keep_logs                      |                                                                 |
|                                |                                                                 |
+--------------------------------+-----------------------------------------------------------------+


