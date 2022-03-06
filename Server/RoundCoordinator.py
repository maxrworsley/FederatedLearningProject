import threading
import time

from FLM import Session
from FLM import MessageDefinitions
from FLM import Connection
import queue


class Coordinator:
    tf_handler = None

    def set_handler(self, handler):
        self.tf_handler = handler

    def start_round(self):
        print("Starting round")
        send_queue, receive_queue = queue.Queue(), queue.Queue()
        local_socket = Connection.get_new_server_socket("", 40400)
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
