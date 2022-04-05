import argparse


class ConfigurationManager:
    run_on_desktop = False
    file_path = "/home/FLS/Node/data.csv"
    working_directory = "/home/FLS/Node/working_directory/"
    local_port = 40401
    remote_ip = "172.17.0.1"
    remote_port = 40400

    def parse_options(self, opt):
        parser = argparse.ArgumentParser()
        parser.add_argument(type=str, help='the script base path', dest='base_directory')
        parser.add_argument('--run_on_desktop', action='store_true')

        args = parser.parse_args(opt)

        if args.run_on_desktop:
            self.run_on_desktop = True
            self.file_path = \
                "/home/max/Documents/FederatedLearning/FederatedLearningProject/Node/data.csv"
            self.working_directory = \
                "/home/max/Documents/FederatedLearning/node_working_directory"
