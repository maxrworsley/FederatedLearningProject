import logging
import os
from sys import argv

import ConfigurationManager
import Node

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.info('Starting')
    config_manager = ConfigurationManager.ConfigurationManager()
    config_manager.parse_options(argv)
    # We don't need warnings about lack of GPU
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

    node = Node.Node()
    node.start(config_manager)
