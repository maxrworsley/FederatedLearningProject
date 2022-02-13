import FLServer
import RoundCoordinator

if __name__ == '__main__':

    coordinator = RoundCoordinator.Coordinator()
    server = FLServer.FLServer(coordinator)
    server.run_server()
