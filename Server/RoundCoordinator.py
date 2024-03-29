import logging
import os
import shutil

from Aggregation import ModelAggregationHandler
from ClientManager import ClientManager
from Visualisation import Visualiser
from FLM import CheckpointHandler
from FLM import Connection
from FLM import MessageDefinitions


class Coordinator:
    """Handles the control flow of the training round, using the handlers.
    Performs and marshals nodes through a single round"""
    tf_handler = None
    keep_running = True
    config_manager = None
    cp_handler = None
    aggregation_handler = None
    local_socket = None
    client_manager = None
    models_received_messages = None
    models_received = []

    def set_handlers(self, tf_handler, config_manager):
        self.tf_handler = tf_handler
        self.config_manager = config_manager

    def setup(self):
        self.cp_handler = CheckpointHandler.CheckpointHandler(self.config_manager.working_directory,
                                                              self.config_manager.remove_directory)
        self.local_socket = Connection.get_new_server_socket("", self.config_manager.working_port)
        self.client_manager = ClientManager(self.local_socket)

    def perform_round(self):
        self.setup()
        logging.info("Completed setup. Starting round")

        self.wait_for_nodes()
        self.send_model()
        self.wait_for_responses()
        self.unpack_responses()
        self.aggregate_models()
        self.plot_responses()
        if not self.keep_running:
            # At some point the round has failed
            self.client_manager.stop_prematurely()

    def wait_for_nodes(self):
        if not self.keep_running:
            return

        try:
            self.client_manager.gather_nodes(self.config_manager.node_count)
        except KeyboardInterrupt:
            logging.warning("Stopping prematurely. Waiting for connections to timeout")
            self.client_manager.keep_gathering_nodes = False
            self.keep_running = False

    def send_model(self):
        if not self.keep_running:
            return

        # If we are in non-persistent mode
        if self.config_manager.remove_directory:
            self.tf_handler.get_model()
        else:
            self.tf_handler.get_model(os.path.join(self.config_manager.working_directory, "model"))

        self.tf_handler.save_current_model(self.config_manager.working_directory)
        self.cp_handler.create_checkpoint()

        logging.info("Sending train model message")
        model_message = MessageDefinitions.RequestTrainModel()
        model_message.checkpoint_bytes = self.cp_handler.get_saved_checkpoint_bytes()
        model_message.epochs = self.config_manager.epochs
        self.client_manager.send_model_to_nodes(model_message)

    def wait_for_responses(self):
        if not self.client_manager.are_any_active():
            logging.info("No nodes connected. Stopping.")
            self.keep_running = False
            return

        logging.info("Waiting for the model to be returned from nodes")

        try:
            self.models_received_messages = self.client_manager.wait_for_models(self.config_manager.training_timeout)
        except KeyboardInterrupt:
            logging.warning("Stopping prematurely. Waiting for timeout.")
            self.keep_running = False
            return

        logging.info("Received following messages from clients:")
        logging.info(self.models_received_messages)

    def unpack_responses(self):
        if not self.keep_running:
            return

        received_model_directory = os.path.join(self.config_manager.working_directory, "received_models")
        for idx, response in enumerate(self.models_received_messages):
            if response:
                # Model number n is saved in the format working_directory/received_models/n/model
                cp_handler = CheckpointHandler.CheckpointHandler(os.path.join(received_model_directory, str(idx)),
                                                                 self.config_manager.remove_directory)
                cp_handler.save_unpack_checkpoint(response.checkpoint_bytes)

                # Add the model to a list to be aggregated
                model = self.tf_handler.load_model(os.path.join(received_model_directory, str(idx), "model"))
                self.models_received.append((model, response.evaluation_loss))

    def aggregate_models(self):
        if not self.keep_running:
            return

        if len(self.models_received) == 0:
            logging.warning("No models received. Cannot perform aggregation")
            self.keep_running = False
            return

        self.aggregation_handler = ModelAggregationHandler(self.models_received)
        selected_model = self.aggregation_handler.aggregate_models()
        if not self.config_manager.remove_directory:
            self.tf_handler.set_model(selected_model)
            self.tf_handler.save_current_model(self.config_manager.working_directory)
        logging.info(f"Aggregated model computed. {selected_model}.")

    def plot_responses(self):
        if not self.keep_running:
            return

        if not self.config_manager.plot_responses:
            return

        visualiser = Visualiser()

        history_with_id = [(message.history, message.sender_id, message.location)
                           for message in self.models_received_messages if message]

        if len(history_with_id) < 1:
            print("Tried to display results but none found")
            return

        visualiser.plot_evaluation_losses(history_with_id)
        visualiser.plot_loss_same_graph(history_with_id, self.config_manager.epochs)
        visualiser.plot_history_over_epochs(history_with_id, self.config_manager.epochs)

    def __del__(self):
        # Clean up
        if self.config_manager.remove_directory:
            try:
                shutil.rmtree(self.config_manager.working_directory)
            except AttributeError:
                # Directory already removed
                pass
        self.local_socket.close()
