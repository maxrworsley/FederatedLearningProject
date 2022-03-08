import time

import ClientTensorflowHandler
from FLM import MessageDefinitions as msg
from ServerManager import ServerManager


class RoundCoordinator:
    configuration_manager = None
    tensorflow_manager = None
    keep_running = True

    def __init__(self, config_manager):
        self.configuration_manager = config_manager
        self.server_manager = ServerManager()
        self.tensorflow_manager = ClientTensorflowHandler.TensorflowHandler()

    def start_round(self):
        self.keep_running = True
        self.server_manager.start()
        self.join_round()
        self.wait_for_model()
        self.train_model()
        self.stop_round()

    def join_round(self):
        while self.keep_running:
            self.server_manager.send_message(msg.RequestJoinRound())

            join_message = self.handle_messages(msg.ResponseJoinRound.id)
            if join_message.accepted_into_round:
                return

            time.sleep(1)

    def wait_for_model(self):
        train_message = self.handle_messages(msg.RequestTrainModel.id)
        if train_message:
            self.tensorflow_manager.received_bytes = train_message.checkpoint_bytes
            return

        self.keep_running = False

    def train_model(self):
        self.tensorflow_manager.train(self.configuration_manager)
        self.server_manager.send_message(msg.ResponseTrainModel())

    def stop_round(self):
        print("Completed training. Disconnecting")
        self.keep_running = False
        self.server_manager.stop()

    def get_message(self):
        message = None
        while message is None and self.keep_running:
            message = self.server_manager.get_next_message()

        return message

    def handle_messages(self, target_id):
        while self.keep_running:
            message = self.get_message()

            if message.id == target_id:
                return message

            self.handle_exceptional_message(message)
        return None

    def handle_exceptional_message(self, message):
        m_id = message.id
        if m_id == msg.StopSession.id:
            self.stop_round()
        elif m_id == msg.CheckConnection.id:
            response = msg.CheckConnectionResponse()
            self.server_manager.send_message(response)
        elif m_id == msg.RoundCancelled.id:
            self.stop_round()
        else:
            print("Received message that couldn't be handled. Stopping")
            print(message)
            self.stop_round()
