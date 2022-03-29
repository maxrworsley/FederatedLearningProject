import FLServer
import RoundCoordinator
import ConfigurationManager
from sys import argv


if __name__ == '__main__':
    config_manager = ConfigurationManager.ConfigurationManager()
    config_manager.parse_options(argv)
    coordinator = RoundCoordinator.Coordinator()
    server = FLServer.FLServer(config_manager, coordinator)
    server.run_server()
