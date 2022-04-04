import os

from FLM import MessageDefinitions
from FLM import Connection
from FLM import CheckpointHandler
from ClientManager import ClientManager
from Aggregation import ModelAggregationHandler


class Coordinator:
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
        self.cp_handler = CheckpointHandler.CheckpointHandler(self.config_manager.working_directory)
        self.local_socket = Connection.get_new_server_socket("", self.config_manager.working_port)
        self.client_manager = ClientManager(self.local_socket)

    def start_round(self):
        self.setup()
        print("Starting round")

        self.wait_for_nodes()
        self.send_model()
        self.wait_for_responses()
        self.unpack_responses()
        self.aggregate_models()

    def wait_for_nodes(self):
        self.client_manager.gather_nodes(2)

    def send_model(self):
        print("Sending train model message")
        model_message = MessageDefinitions.RequestTrainModel()
        self.tf_handler.create_model()
        self.tf_handler.save_current_model(self.config_manager.working_directory)
        self.cp_handler.create_checkpoint()
        model_message.checkpoint_bytes = self.cp_handler.get_saved_checkpoint_bytes()
        model_message.epochs = 1
        self.client_manager.send_model_to_nodes(model_message)

    def wait_for_responses(self):
        if not self.client_manager.are_any_active():
            print("Lost all clients. Stopping")
            self.keep_running = False
            return

        print("Waiting for the model to be returned")
        self.models_received_messages = self.client_manager.wait_for_node_models()
        print(self.models_received_messages)

    def unpack_responses(self):
        received_model_directory = os.path.join(self.config_manager.working_directory, "received_models")
        for idx, response in enumerate(self.models_received_messages):
            if response:
                # Model number n is saved in the format working_directory/received_models/n/model
                cp_handler = CheckpointHandler.CheckpointHandler(os.path.join(received_model_directory, str(idx)))
                cp_handler.save_unpack_checkpoint(response.checkpoint_bytes)
                model = self.tf_handler.load_model(os.path.join(received_model_directory, str(idx), "model"))
                self.models_received.append((model, response.evaluation_loss))

    def aggregate_models(self):
        self.aggregation_handler = ModelAggregationHandler(self.models_received)
        selected_model = self.aggregation_handler.aggregate_models()
        print(selected_model)

    def __del__(self):
        self.local_socket.close()
