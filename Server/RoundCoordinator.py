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

    def set_handler(self, tf_handler, config_manager):
        self.tf_handler = tf_handler
        self.config_manager = config_manager

    def setup(self):
        pass

    def start_round(self):
        cp_handler = CheckpointHandler.CheckpointHandler(self.config_manager.working_directory)

        print("Starting round")
        send_queue, receive_queue = queue.Queue(), queue.Queue()
        local_socket = Connection.get_new_server_socket("", self.config_manager.working_port)
        server_session = Session.ServerSessionManager(send_queue, receive_queue, local_socket)
        server_thread = threading.Thread(target=server_session.start)
        server_thread.start()

        # Receive request join round
        join_round_request = receive_queue.get(block=True)
        print(join_round_request)
        print("Responding to join round")
        accepted_into_round_message = self.add_message_attributes(MessageDefinitions.ResponseJoinRound())
        send_queue.put(accepted_into_round_message)

        print("Sending train model message")
        model_message = self.add_message_attributes(MessageDefinitions.RequestTrainModel())
        self.tf_handler.create_model()
        self.tf_handler.save_current_model(self.config_manager.working_directory)
        cp_handler.create_checkpoint()
        model_message.checkpoint_bytes = cp_handler.get_saved_checkpoint_bytes()
        send_queue.put(model_message)

        # Receive model back
        print("Waiting for the model to be returned")
        model_received = receive_queue.get(block=True)
        print(model_received)

        server_thread.join()
        local_socket.close()

    @staticmethod
    def add_message_attributes(message):
        message.sender_id = 1
        message.receiver_id = 3
        message.round_id = 1
        message.time_sent = time.time()
        return message

    def wait_for_nodes(self):
        pass

    def send_model(self):
        pass

    def wait_for_responses(self):
        pass

    def aggregate_models(self):
        pass

