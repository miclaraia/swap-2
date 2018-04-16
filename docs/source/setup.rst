
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

    config.annotation.update({'task': 'T1', 'true': ['Real', 'Yes', 1], 'false': ['Bogus', 'No', 0]})

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

    `swap run ${NAME} ${CLASSIFICATION_DUMP}


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

Online swap queries classifications from the panoptes api and sends them
to a placeholder reducer in caesar. Make sure caesar_external is properly 
setup for this project, then configure online swap with:
`swap online config ${NAME} ${CAESAR_NAME}` Where `${CAESAR_NAME}` is the name
used to configure the caesar_external library for this project.

Then run swap online with::

    swap online run ${NAME}

This will fetch the most recent classifications from the panoptes api, run swap on the data,
then determine retirement thresholds, and send swap scores back to caesar.