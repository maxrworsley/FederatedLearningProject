import argparse
import logging


class ConfigurationManager:
    working_directory = "/home/max/Documents/FederatedLearning/server_working_directory"
    working_port = 40400
    node_count = 1
    remove_directory = False
    plot_responses = False
    epochs = 1
    training_timeout = 60

    def parse_options(self, opt):
        parser = argparse.ArgumentParser()
        parser.add_argument(type=str, help='the script base path', dest='base_directory')
        parser.add_argument('--local_port', type=int, required=False)
        parser.add_argument('--node_count', type=int, required=False)
        parser.add_argument('--epochs', type=int, required=False)
        parser.add_argument('--training_timeout', type=int, required=False)
        parser.add_argument('-rm', action='store_true', dest='remove_directory')
        parser.add_argument('--plot', action='store_true', dest='plot')

        args = parser.parse_args(opt)

        if args.local_port:
            self.working_port = args.local_port

        if args.node_count:
            self.node_count = args.node_count

        if args.plot:
            self.plot_responses = True

        if args.epochs:
            self.epochs = args.epochs

        if args.training_timeout:
            self.training_timeout = args.training_timeout

        if args.remove_directory:
            self.remove_directory = True

        logging.info(f"Working on local port {self.working_port}. Node count is {self.node_count}.")
