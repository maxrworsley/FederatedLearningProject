import threading
import time
import queue

from FLM import Session
from FLM import MessageDefinitions
from FLM import Connection
from FLM import CheckpointHandler


class Coordinator:
    tf_handler = None
    keep_running = True
    config_manager = None
    cp_handler = None
    send_queue = None
    receive_queue = None
    local_socket = None

    def set_handlers(self, tf_handler, config_manager):
        self.tf_handler = tf_handler
        self.config_manager = config_manager

    def setup(self):
        self.cp_handler = CheckpointHandler.CheckpointHandler(self.config_manager.working_directory)
        self.send_queue, self.receive_queue = queue.Queue(), queue.Queue()
        self.local_socket = Connection.get_new_server_socket("", self.config_manager.working_port)

    def start_round(self):
        self.setup()
        print("Starting round")
        server_session = Session.ServerSessionManager(self.send_queue, self.receive_queue, self.local_socket)
        session_manager_thread = threading.Thread(target=server_session.start)
        session_manager_thread.start()

        self.wait_for_nodes()
        self.send_model()
        self.wait_for_responses()
        self.aggregate_models()

        session_manager_thread.join()

    @staticmethod
    def add_message_attributes(message):
        message.sender_id = 1
        message.receiver_id = 3
        message.round_id = 1
        message.time_sent = time.time()
        return message

    def wait_for_nodes(self):
        # Receive request join round
        join_round_request = self.receive_queue.get(block=True)
        print(join_round_request)
        print("Responding to join round")
        accepted_into_round_message = self.add_message_attributes(MessageDefinitions.ResponseJoinRound())
        self.send_queue.put(accepted_into_round_message)

    def send_model(self):
        print("Sending train model message")
        model_message = self.add_message_attributes(MessageDefinitions.RequestTrainModel())
        self.tf_handler.create_model()
        self.tf_handler.save_current_model(self.config_manager.working_directory)
        self.cp_handler.create_checkpoint()
        model_message.checkpoint_bytes = self.cp_handler.get_saved_checkpoint_bytes()
        model_message.epochs = 1
        self.send_queue.put(model_message)

    def wait_for_responses(self):
        # Receive model back
        print("Waiting for the model to be returned")
        model_received = self.receive_queue.get(block=True)
        print(model_received)

    def aggregate_models(self):
        pass

    def __del__(self):
        self.local_socket.close()
