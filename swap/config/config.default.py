
# Copy the contents of this file to config.py to override config
# options


def override(config):

    # Configuration for Online Swap
    # config.database.name = 'ghosts_test'

    # Configuration for Annotation parser
    # config.parser.annotation.task = 'T0'
    # config.parser.annotation.true = ['Yes', 1]
    # config.parser.annotation.false = ['No', 0]

    # Workflow id
    # config.online_swap.workflow = 3004

    # SWAP host machine address
    # config.online_swap.host = 'northdown.spa.umn.edu'
    # config.online_swap.ext_port = '443'

    # Address configuration to access caesar and panoptes
    # config.online_swap.caesar.caesar_endpoint = 'caesar-staging'
    # config.online_swap.caesar.panoptes_endpoint = 'panoptes-staging'
    # config.online_swap.caesar.port = '443'


    # config.logging.files.version = 'static'

    # True: static swap, False: dynamic swap
    # config.back_update = True

    # Prior probability
    # config.p0 = 0.12

    # Acceptable missed detection rate for retirement thresholds
    # config.mdr = 0.1

    # Database configuration
    # config.database.name = 'swapDB'
    # config.database.host = 'localhost'
    # config.database.port = 27017

    return None
