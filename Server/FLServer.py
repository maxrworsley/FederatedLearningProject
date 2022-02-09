class FLServer:
    def __init__(self, name, tf_handler):
        self.name = name
        self.tf_handler = tf_handler

    def run_server(self):
        print(f'Server running. Name = {self.name}')
