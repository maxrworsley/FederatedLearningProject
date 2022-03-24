import ServerTensorflowHandler


class FLServer:
    def __init__(self, config_manager, coordinator):
        self.configuration = config_manager
        self.coordinator = coordinator
        tf_handler = ServerTensorflowHandler.TensorflowHandler()
        self.coordinator.set_handlers(tf_handler, self.configuration)

    def run_server(self):
        self.coordinator.start_round()
