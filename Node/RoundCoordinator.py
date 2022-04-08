import logging
import threading

from FLM import MessageDefinitions as msg
from ClientTensorflowHandler import TensorflowHandler
from ServerManager import ServerManager


class RoundCoordinator:
    """Main class that controls the program flow of the node.
    Joins together handlers and managers to perform a single round"""
    config_manager = None
    tf_manager = None
    keep_running = True
    receive_async_messages = True

    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.server_manager = ServerManager(config_manager)
        self.tf_manager = TensorflowHandler()

    def perform_round(self):
        self.keep_running = True
        self.server_manager.start(self.cancel_callback)
        self.join_round()
        self.wait_for_model()
        self.train_model()
        self.stop_round()

    def cancel_callback(self):
        # Used to cancel round due to no connection if required
        self.keep_running = False

    def join_round(self):
        if not self.keep_running:
            return

        logging.info("Attempt to join round.")
        self.server_manager.send_message(msg.RequestJoinRound())

        join_message = self.handle_messages(msg.ResponseJoinRound.id)
        if join_message:
            if join_message.accepted_into_round:
                logging.info("Joined round")
                return
            else:
                logging.info("Unexpected response to join round request")
        else:
            logging.info("No response to join round request")

    def wait_for_model(self):
        if not self.keep_running:
            return

        train_message = None

        while not train_message and self.keep_running:
            train_message = self.handle_messages(msg.RequestTrainModel.id)
            if train_message:
                # Set the configuration for training using the message parameters
                self.tf_manager.received_bytes = train_message.checkpoint_bytes
                self.tf_manager.training_epochs = train_message.epochs
                self.tf_manager.validation_split = train_message.validation_split
                return

        self.keep_running = False

    def train_model(self):
        if not self.keep_running:
            return

        # Keep a thread running to receive messages such as cancellation
        receive_messages_thread = threading.Thread(target=self.async_message_handler)
        receive_messages_thread.start()

        # Train model
        self.tf_manager.train(self.config_manager)
        self.receive_async_messages = False
        receive_messages_thread.join()

        # Send model back
        response_message = msg.ResponseTrainModel()
        response_message.checkpoint_bytes = self.tf_manager.get_model_bytes_remove_directory(self.config_manager)
        response_message.history = self.tf_manager.get_most_recent_history()
        self.server_manager.send_message(response_message)

    def stop_round(self):
        logging.info("Stopping")
        self.receive_async_messages = False
        self.keep_running = False
        self.tf_manager.stop_training()
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
            if message:
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
