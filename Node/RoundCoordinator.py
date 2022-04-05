import logging
import threading
import time

import ClientTensorflowHandler
from FLM import MessageDefinitions as msg
from ServerManager import ServerManager


class RoundCoordinator:
    configuration_manager = None
    tensorflow_manager = None
    keep_running = True
    receive_async_messages = True

    def __init__(self, config_manager):
        self.configuration_manager = config_manager
        self.server_manager = ServerManager(config_manager)
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
            logging.info("Attempt to connect to server.")
            self.server_manager.send_message(msg.RequestJoinRound())

            join_message = self.handle_messages(msg.ResponseJoinRound.id)
            if join_message:
                if join_message.accepted_into_round:
                    return
            else:
                logging.info("Received unexpected response to join round request")

            time.sleep(1)

    def wait_for_model(self):
        train_message = None
        while not train_message and self.keep_running:
            train_message = self.handle_messages(msg.RequestTrainModel.id)
            if train_message:
                self.tensorflow_manager.received_bytes = train_message.checkpoint_bytes
                self.tensorflow_manager.training_epochs = train_message.epochs
                self.tensorflow_manager.validation_split = train_message.validation_split
                return

        self.keep_running = False

    def train_model(self):
        message_thread = threading.Thread(target=self.async_message_handler)
        message_thread.start()
        self.tensorflow_manager.train(self.configuration_manager)
        self.receive_async_messages = False
        message_thread.join()
        response_message = msg.ResponseTrainModel()
        response_message.checkpoint_bytes = \
            self.tensorflow_manager.get_model_bytes_remove_directory(self.configuration_manager)
        self.server_manager.send_message(response_message)

    def stop_round(self):
        logging.info("Completed training. Disconnecting")
        self.receive_async_messages = False
        self.keep_running = False
        self.tensorflow_manager.stop_training()
        self.server_manager.stop()

    def get_message(self):
        message = None
        while message is None and self.keep_running:
            message = self.server_manager.get_next_message()

        return message

    def async_message_handler(self):
        self.receive_async_messages = True
        while self.receive_async_messages and self.keep_running:
            message = None

            while message is None and self.receive_async_messages and self.keep_running:
                message = self.server_manager.get_next_message()

            if message:
                self.handle_exceptional_message(message)

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
            logging.error("Received message that couldn't be handled. Stopping")
            logging.error(message)
            self.stop_round()
