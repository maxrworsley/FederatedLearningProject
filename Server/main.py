import logging
import os
from sys import argv

import ConfigurationManager
import FLServer
import RoundCoordinator

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.info('Starting')
    config_manager = ConfigurationManager.ConfigurationManager()
    config_manager.parse_options(argv)
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

    coordinator = RoundCoordinator.Coordinator()
    server = FLServer.FLServer(config_manager, coordinator)
    server.run_server()
