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
        self.server_manager.send_message(msg.RequestJoinRound())
        while self.keep_running:
            message = self.get_message()

            if message.id != msg.ResponseJoinRound.id:
                print("Received an unexpected reply from request to join round")
                print(message)
                self.keep_running = False
                return

            print(message.accepted_into_round)
            if message.accepted_into_round:
                return

            time.sleep(0.5)

    def wait_for_model(self):
        while self.keep_running:
            message = self.get_message()
            m_id = message.id
            if m_id == msg.RequestTrainModel.id:
                self.tensorflow_manager.received_bytes = message.checkpoint_bytes
                break
            else:
                self.handle_exceptional_message(message)
        
    def train_model(self):
        while self.keep_running:
            message = self.get_message()
            if message.id == msg.RequestTrainModel.id:
                self.tensorflow_manager.train(self.configuration_manager.file_path)
                self.server_manager.send_message(msg.ResponseJoinRound())
                break
            else:
                self.handle_exceptional_message(message)

    def stop_round(self):
        print("Completed training. Disconnecting")
        self.keep_running = False
        self.server_manager.stop()

    def get_message(self):
        message = None
        while message is None and self.keep_running:
            message = self.server_manager.get_next_message()

        return message

    def handle_exceptional_message(self, message):
        message_id = message.id
        if message_id == msg.StopSession.id:
            self.stop_round()
        elif message_id == msg.CheckConnection.id:
            response = msg.CheckConnectionResponse()
            self.server_manager.send_message(response)
        elif message_id == msg.RoundCancelled.id:
            self.stop_round()
        else:
            print("Received message that couldn't be handled. Stopping")
            print(message)
            self.stop_round()
