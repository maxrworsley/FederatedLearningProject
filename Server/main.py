import FLServer
import RoundCoordinator
import ConfigurationManager
from sys import argv
import os


if __name__ == '__main__':
    config_manager = ConfigurationManager.ConfigurationManager()
    config_manager.parse_options(argv)
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    coordinator = RoundCoordinator.Coordinator()
    server = FLServer.FLServer(config_manager, coordinator)
    server.run_server()
