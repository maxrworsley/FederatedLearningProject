from FLM import MessageDefinitions
from FLM import Connection
from FLM import CheckpointHandler
from ClientManager import ClientManager


class Coordinator:
    tf_handler = None
    keep_running = True
    config_manager = None
    cp_handler = None
    local_socket = None
    client_manager = None

    def set_handlers(self, tf_handler, config_manager):
        self.tf_handler = tf_handler
        self.config_manager = config_manager

    def setup(self):
        print("Beginning setup")
        self.cp_handler = CheckpointHandler.CheckpointHandler(self.config_manager.working_directory)
        self.local_socket = Connection.get_new_server_socket("", self.config_manager.working_port)
        self.client_manager = ClientManager(self.local_socket)

    def start_round(self):
        self.setup()
        print("Starting round")

        self.wait_for_nodes()
        self.send_model()
        self.wait_for_responses()
        self.aggregate_models()

    def wait_for_nodes(self):
        print("Gathering nodes")
        self.client_manager.gather_nodes(1)

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
        print("Waiting for the model to be returned")
        models_received = self.client_manager.wait_for_node_models()
        print(models_received)

    def aggregate_models(self):
        pass

    def __del__(self):
        self.local_socket.close()
