class ConfigurationManager:
    run_on_desktop = False
    file_path = "/home/FLS/Node/data.csv"
    working_directory = "/home/FLS/Node/working_directory/"
    local_port = 40401
    remote_ip = "172.17.0.1"
    remote_port = 40400

    def parse_options(self, opt):
        if len(opt) > 1:
            if opt[1] == "-d" or opt[1] == "-D":
                self.run_on_desktop = True
                self.file_path = \
                    "/home/max/Documents/FederatedLearning/FederatedLearningProject/Node/data.csv"
                self.working_directory = \
                    "/home/max/Documents/FederatedLearning/node_working_directory"
