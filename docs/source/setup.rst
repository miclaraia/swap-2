
Getting Started
===============

The SWAP algorithm was developed by [Phil Marshall et al.](https://github.com/drphilmarshall/SpaceWarps/raw/master/doc/sw-system-published.pdf), and the original implementation of the algorithm that provided the motivation for this work can be found [here](https://github.com/drphilmarshall/SpaceWarps).

The [caesar_external](https://github.com/miclaraia/caesar_external) library provides functionality for interacting with live classifications from Panoptes and Caesar in the Zooniverse. Installing this library activates these features in swap.

Installation
------------

Automatic Installation
~~~~~~~~~~~~~~~~~~~~~~

Clone the repository::

    git clone https://github.com/zooniverse/swap.git

Install with python pip::
    
    pip install -e swap

We recommend doing this in a virtual environment, so use whatever method suits you to set that up.


Configuring SWAP
----------------

SWAP can be used with multiple projects at the same time, each project must have its own unique identifier. This identifier should be used anywhere that ${NAME} shows up, and is completely arbitrary.

To configure a new project with swap, start with the command::

    swap new ${NAME} --config

This will bring up a python interpreter, which you can use to interact with the `config` object. The config object lets you set configure how swap should parse the csv classification dump from panoptes. Each project will have a different task key, and different labels that are used in the actual classification. The config annotation field has subfields `'task'`, `'true'`, and `'false'` to configure this. This is an example of how this might be set up::

    config.annotation.update({
        'task': 'T1', 'true': ['Real', 'Yes', 1], 'false': ['Bogus', 'No', 0]
    })

Other configuration options:

+-----------------------------------+----------------------------------------------------------+
| Name                              | Description                                              |
+===================================+==========================================================+
| config.annotation.task            | Task label, like T0, T1, ...                             |
+-----------------------------------+----------------------------------------------------------+
| config.annotation.value_key       |                                                          |
+-----------------------------------+----------------------------------------------------------+
| config.annotation.value_separator |                                                          |
+-----------------------------------+----------------------------------------------------------+
| config.annotation.true            | Expected classification value for a real detection.      |
+-----------------------------------+----------------------------------------------------------+
| config.annotation.false           | Expected classification value for a bogus detection      |
+-----------------------------------+----------------------------------------------------------+
| config.mdr                        | Missed detection rate used to draw the decision          |
|                                   | boundaries for retirement.                               |
+-----------------------------------+----------------------------------------------------------+
| config.fpr                        | False Positive rate used to draw the decision boundaries |
|                                   | for retirement.                                          |
+-----------------------------------+----------------------------------------------------------+

Running SWAP
------------

Start by initializing swap's gold labels by running::

    swap golds ${NAME} ${GOLDS_CSV_FILE}

The csv file should have two columns labeled `subject` and `gold`. The gold label column should have
a `1` for real subjects and a `0` for bogus subjects. Only one row per subject.

Then run swap on a panoptes csv dump with::

    swap run ${NAME} ${CLASSIFICATION_DUMP}


If swap runs out of memory during the process, you can split the csv into batches in a script
and run `swap.truncate()` between batches. This clears the classification history for each
user and subject tracked by swap, keeping only enough information to use as priors and keep
making accurate predictions.

.. note:: Note that in order to preserve memory and time, SWAP first loads classifications
from the csv dump, then updates all the user scores at once, then updates all subject scores
using the resulting user scores. This is different from how SWAP was originally envisioned
in literature, but this is faster and saves resources.

A lot of the swap ui commands end by opening a python interpreter, which allows you to
inspect the resulting data before closing. The resulting scores are automatically saved
on each run, which pickles a json blob of the configuration, subject data, user data,
and the score thresholds used for retirement decisions.

Online swap
-----------

Swap can be configured to run in online mode, where it queries classifications from zooniverse and sends swap scores as reductions to caesar. The classifications can either be queried through the panoptes api, or through caesar in conjunction with Amazon's Simple Queue Service.

Start by deciding how you will authenticate with zooniverse. You'll probably either want to configure this to use environment variables containing your Zooniverse username and password, or configure to use an OAuth client id and secret pair. Alternatively you will be asked for your zooniverse username and password every time a command is run. Store username and password in :code:`$PANOPTES_USERNAME` and :code:`$PANOPTES_PASSWORD`, and store client id and secret in :code:`$PANOPTES_CLIENT_SECRET` and :code:`$PANOPTES_CLIENT_ID`. API keys can be generated through the `Zooniverse OAuth provider <https://panoptes.zooniverse.org/oauth/applications>`_ with :code:`urn:ietf:wg:oauth:2.0:oob` as the callback URI.

Next you should run the configuration command. The syntax for the command is described below. To configure this module to get classifications from caesar, specify the sqs queue caesar has been configured to dump classifications into. If this is not specified then classifications will be fetched from panoptes. Caesar must be configured to accept reductions from an external source using a placeholder reducer. The name given to the reducer in caesar's config should be entered for :code:`caeesar_name`.


Caesar Config Command Reference
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: none

    Usage: caesar config new [OPTIONS] NAME PROJECT WORKFLOW

      Generate new configuration for a project.

      Arguments
      ---------
      name - Arbitrary name used to store configuration
      project - Zooniverse project id
      workflow - Zooniverse workflow id

    Options:
      --last_id INTEGER   Exclude classifications before this classification id.
      --caesar_name TEXT  Name used for swap as a reducer in caesar's
                          configuration, see
                          https://zooniverse.github.io/caesar/#introduction about
                          setting up a reducer in caesar.
      --sqs_queue TEXT    Specify whether caesar should subscribe to an SQS queue
                          for classifications. If left blank will default to
                          panoptes api as classification source.
      --staging           Flag to use staging endpoints for panoptes and caesar
      --auth_mode TEXT    interactive,environment,api_key
                          If api_key is selected,
                          make sure client id and client secret are stored in
                          environment variables in PANOPTES_CLIENT_ID and
                          PANOPTES_CLIENT_SECRET
      --help              Show this message and exit.

Now point swap to the right caesar_external configuration you just set up. The command to do this is specified below.

.. code-block:: none

    Usage: swap online config [OPTIONS] NAME ONLINE_NAME

      Configure swap to use caesar external configuration

      Arguments
      ---------
      name - Name of swap configuration
      online-name - Name of caesar_external configuration

    Options:
      --help  Show this message and exit.


Finally run swap in online mode. You can use either of the following commands. The first fetches all classifications and posts reductions. The second runs the process in a loop (WARNING this is still experimental).

.. code-block:: bash

    swap online run ${NAME}
    swap online run_continuous ${NAME}