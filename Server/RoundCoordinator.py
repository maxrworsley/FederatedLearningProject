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
        # self.tf_handler.get_data()

        # self.tf_handler.create_model()
        # self.tf_handler.fit_model(50)
        send_queue, receive_queue = queue.Queue(), queue.Queue()
        local_socket = Connection.get_new_server_socket("", 40400)
        server_session = Session.ServerSessionManager(send_queue, receive_queue, local_socket)
        server_thread = threading.Thread(target=server_session.start)
        server_thread.start()

        send_message = MessageDefinitions.RequestTrainModel()
        send_message.sender_id = 1
        send_message.round_id = 1
        send_message.receiver_id = 3
        send_message.time_sent = time.time()
        send_queue.put(send_message)

        message_received = receive_queue.get(block=True)
        print(message_received)
        server_thread.join()
        local_socket.close()
