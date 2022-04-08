import argparse
import os.path


class ConfigurationManager:
    run_on_desktop = False
    file_path = "/home/FLS/Node/data.csv"
    working_directory = "/home/FLS/Node/working_directory/"
    remote_ip = "172.17.0.1"
    remote_port = 40400
    local_port = 40401

    def parse_options(self, opt):
        parser = argparse.ArgumentParser()
        parser.add_argument(type=str, help='the script base path', dest='base_directory')
        parser.add_argument('--run_on_desktop_extension', type=str, required=False)

        args = parser.parse_args(opt)

        if args.run_on_desktop_extension:
            self.run_on_desktop = True
            self.file_path = "/home/max/Documents/FederatedLearning/FederatedLearningProject/Node/data.csv"
            self.working_directory = os.path.join("/home/max/Documents/FederatedLearning/node_working_directory",
                                                  args.run_on_desktop_extension)
