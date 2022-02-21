import ServerTensorflowHandler


class FLServer:
    def __init__(self, coordinator):
        self.coordinator = coordinator
        tf_handler = ServerTensorflowHandler.TensorflowHandler()
        self.coordinator.set_handler(tf_handler)

    def run_server(self):
        self.coordinator.start_round()
