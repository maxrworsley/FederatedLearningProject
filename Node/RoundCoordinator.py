from FLM import MessageDefinitions
from ServerManager import ServerManager
import ClientTensorflowHandler
import queue


class RoundCoordinator:
    send_q = None
    receive_q = None
    configuration_manager = None
    tensorflow_manager = None

    def __init__(self, config_manager):
        self.configuration_manager = config_manager
        self.send_q, self.receive_q = queue.Queue(), queue.Queue()
        self.server_manager = ServerManager(self.send_q, self.receive_q)

    def start_round(self):
        self.server_manager.start()
        success = self.train()

        self.stop_round(success)

    def stop_round(self, round_success):
        if round_success:
            print("Completed training successfully. Disconnecting")
        else:
            print("Training did not complete successfully. Disconnecting")

        self.server_manager.stop()

    def train(self):
        tf_handler = ClientTensorflowHandler.TensorflowHandler()

        message = self.receive_q.get(block=True)
        if message.id != MessageDefinitions.RequestTrainModel.id:
            return False

        tf_handler.train(self.configuration_manager.file_path)
        self.send_q.put(MessageDefinitions.ResponseJoinRound(0, 0, 0, 0))
        return True
