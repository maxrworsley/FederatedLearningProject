import queue
import threading
import time

from FLM import MessageDefinitions
from FLM import Session


class NodeWrapper:
    send_queue = None
    receive_queue = None
    server_session = None
    session_thread = None
    round_id = -1
    sender_id = -1
    receiver_id = -1
    active = False

    def __init__(self, local_socket):
        self.send_queue, self.receive_queue = queue.Queue(), queue.Queue()
        self.server_session = Session.ServerSessionManager(self.send_queue, self.receive_queue, local_socket)

    def start(self):
        self.session_thread = threading.Thread(target=self.server_session.start)
        self.session_thread.start()

    def send(self, message):
        message.time_sent = time.time()
        message.round_id = self.round_id
        message.sender_id = self.sender_id
        message.receiver_id = self.receiver_id
        self.send_queue.put(message)

    def receive(self, block=False):
        try:
            message = self.receive_queue.get(block=block)
        except queue.Empty:
            message = None

        return message

    def stop(self):
        self.session_thread.join()

    def stop_premature(self):
        self.send_queue.put(MessageDefinitions.StopSession())
        self.session_thread.join(timeout=1)
