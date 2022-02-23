import queue

import ClientTensorflowHandler
from FLM import MessageDefinitions
from ServerManager import ServerManager


class RoundCoordinator:
    configuration_manager = None
    tensorflow_manager = None

    def __init__(self, config_manager):
        self.configuration_manager = config_manager
        self.server_manager = ServerManager()

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
        message = None
        while message is None:
            message = self.server_manager.get_next_message()

        if message.id != MessageDefinitions.RequestTrainModel.id:
            return False

        tf_handler.train(self.configuration_manager.file_path)
        self.server_manager.send_message(MessageDefinitions.ResponseJoinRound(0, 0, 0, 0))
        return True
