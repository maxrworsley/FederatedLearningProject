import argparse


class ConfigurationManager:
    working_directory = "/home/max/Documents/FederatedLearning/server_working_directory"
    working_port = 40400
    node_count = 1

    def parse_options(self, opt):
        parser = argparse.ArgumentParser()
        parser.add_argument(type=str, help='the script base path', dest='base_directory')
        parser.add_argument('--local_port', type=int, required=False)
        parser.add_argument('--node_count', type=int, required=False)

        args = parser.parse_args(opt)

        if args.local_port:
            self.working_port = args.local_port

        if args.node_count:
            self.node_count = args.node_count

        print(f"Working on local port {self.working_port}.")
