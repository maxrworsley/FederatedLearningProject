from sys import argv
import os

import ConfigurationManager
import Node

if __name__ == '__main__':
    config_manager = ConfigurationManager.ConfigurationManager()
    config_manager.parse_options(argv)
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    print(f"Running tensorflow and FLM with run_on_desktop set to {config_manager.run_on_desktop}")
    node = Node.Node()
    node.start(config_manager)
