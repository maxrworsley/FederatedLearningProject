import time
from FLM import MessageDefinitions
from FLM import Connection
from FLM import CheckpointHandler
import NodeWrapper


class Coordinator:
    tf_handler = None
    keep_running = True
    config_manager = None
    cp_handler = None
    local_socket = None
    node = None

    def set_handlers(self, tf_handler, config_manager):
        self.tf_handler = tf_handler
        self.config_manager = config_manager

    def setup(self):
        self.cp_handler = CheckpointHandler.CheckpointHandler(self.config_manager.working_directory)
        self.local_socket = Connection.get_new_server_socket("", self.config_manager.working_port)
        self.node = NodeWrapper.NodeWrapper(self.local_socket)

    def start_round(self):
        self.setup()
        print("Starting round")
        self.node.start()

        self.wait_for_nodes()
        self.send_model()
        self.wait_for_responses()
        self.aggregate_models()

        self.node.stop()

    @staticmethod
    def add_message_attributes(message):
        message.sender_id = 1
        message.receiver_id = 3
        message.round_id = 1
        message.time_sent = time.time()
        return message

    def wait_for_nodes(self):
        join_round_request = self.node.receive(block=True)
        print("Responding to join round")
        accepted_into_round_message = self.add_message_attributes(MessageDefinitions.ResponseJoinRound())
        self.node.send(accepted_into_round_message)

    def send_model(self):
        print("Sending train model message")
        model_message = self.add_message_attributes(MessageDefinitions.RequestTrainModel())
        self.tf_handler.create_model()
        self.tf_handler.save_current_model(self.config_manager.working_directory)
        self.cp_handler.create_checkpoint()
        model_message.checkpoint_bytes = self.cp_handler.get_saved_checkpoint_bytes()
        model_message.epochs = 1
        self.node.send(model_message)

    def wait_for_responses(self):
        print("Waiting for the model to be returned")
        model_received = self.node.receive(block=True)
        print(model_received)

    def aggregate_models(self):
        pass

    def __del__(self):
        self.local_socket.close()
