import ServerTensorflowHandler
import DataWrapper


class FLServer:
    def __init__(self, coordinator):
        self.coordinator = coordinator
        data_wrapper = DataWrapper.DataWrapper("/home/max/Documents/FederatedLearning/Data/data.csv")
        tf_handler = ServerTensorflowHandler.TensorflowHandler("BasicHandler", data_wrapper)
        self.coordinator.set_handler(tf_handler)

    def run_server(self):
        self.coordinator.start_round()
