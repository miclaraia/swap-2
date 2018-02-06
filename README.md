README
======

Make sure desired versions of panoptes_python_client and caesar_external are
installed before attempting to install swap-2

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
