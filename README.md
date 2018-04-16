README
======

Full documentation is available [here](https://zooniverse.github.io/swap/)

The SWAP algorithm was developed by [Phil Marshall et al.](https://github.com/drphilmarshall/SpaceWarps/raw/master/doc/sw-system-published.pdf), and the original implementation of the algorithm that provided the motivation for this work can be found [here](https://github.com/drphilmarshall/SpaceWarps).

The [caesar_external](https://github.com/miclaraia/caesar_external) library provides functionality for interacting with live classifications from Panoptes and Caesar in the Zooniverse. Installing this library activates these features in swap.

Configuration
-------------

`swap new ${NAME}` where ${NAME} is arbitrary. To configure the annotation
parser, pass the `--config` flag, and then enter the desired configuration.
For example, for Supernova Hunters, enter:

`config.annotation.update({'task': 'T1', 'true': ['Real', 'Yes', 1], 'false':
['Bogus', 'No', 0]})`


Running swap
------------

Start by initializing swap's gold labels by running `swap golds ${NAME}
${GOLDS_CSV_FILE}` where ${NAME} is the name used to configure swap, and the
golds csv file contains the gold labels with column labels 'subject', and
'gold'.

Then run swap on a panoptes csv dump with `swap run ${NAME}
${CLASSIFICATION_DUMP}`.


If memory is an issue, split the csv dump into batches, and run
`swap.truncate()` in the python terminal between batches. This truncates the 
score history from the user and subject agents, but maintains enough
information for the swap algorithm to continue functioning.


Online swap
-----------

Online swap queries classifications from the panoptes api and sends them
to a placeholder reducer in caesar. Make sure caesar_external is properly 
setup for this project, then configure online swap with:
`swap online config ${NAME} ${CAESAR_NAME}` Where `${CAESAR_NAME}` is the name
used to configure the caesar_external library for this project.

Then run swap online with `swap online run ${NAME}`.
