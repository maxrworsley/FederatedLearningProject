import queue
import time

import ClientTensorflowHandler
from FLM import MessageDefinitions
from ServerManager import ServerManager


class RoundCoordinator:
    configuration_manager = None
    tensorflow_manager = None
    keep_running = True

    def __init__(self, config_manager):
        self.configuration_manager = config_manager
        self.server_manager = ServerManager()

    def start_round(self):
        self.keep_running = True
        self.server_manager.start()
        self.join_round()
        self.wait_for_model()
        self.train_model()
        self.stop_round()

    def join_round(self):
        joined = False

        while not joined and self.keep_running:
            join_round_message = MessageDefinitions.RequestJoinRound()
            self.server_manager.send_message(join_round_message)
            message = self.get_message()
            if message.id != MessageDefinitions.ResponseJoinRound.id:
                return

            if message.accepted_into_round:
                return

            time.sleep(1)

    def wait_for_model(self):
        if not self.keep_running:
            return

    def train_model(self):
        if not self.keep_running:
            return

        tf_handler = ClientTensorflowHandler.TensorflowHandler()

        message = self.get_message()
        if message.id != MessageDefinitions.RequestTrainModel.id:
            return False

        tf_handler.train(self.configuration_manager.file_path)
        self.server_manager.send_message(MessageDefinitions.ResponseJoinRound())
        return True

    def stop_round(self):
        print("Completed training. Disconnecting")
        self.server_manager.stop()

    def get_message(self):
        message = None
        while message is None and self.keep_running:
            message = self.server_manager.get_next_message()

        return message
