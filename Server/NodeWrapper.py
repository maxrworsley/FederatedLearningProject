import queue
import threading
import time

from FLM import MessageDefinitions
from FLM import Session


class ThreadConnectionCommunicator:
    success = False
    terminate_early = False
    timeout = 5


class NodeWrapper:
    """Wraps a node to make communication easier"""
    send_queue = None
    receive_queue = None
    server_session = None
    session_thread = None
    round_id = -1
    sender_id = -1
    receiver_id = -1
    active = False
    connection_status = None

    def __init__(self, local_socket):
        self.send_queue, self.receive_queue = queue.Queue(), queue.Queue()
        self.server_session = Session.ServerSessionManager(self.send_queue, self.receive_queue, local_socket)
        self.connection_status = ThreadConnectionCommunicator()

    def start(self):
        self.session_thread = threading.Thread(target=self.server_session.start, args=(self.connection_status, ))
        self.session_thread.start()

    def send(self, message):
        message.time_sent = time.time()
        message.round_id = self.round_id
        message.sender_id = self.sender_id
        message.receiver_id = self.receiver_id

        self.send_queue.put(message)

    def receive(self, block=False, timeout=30):
        start_time = time.time()
        elapsed_time = 0
        message = None

        while elapsed_time < timeout and block:
            elapsed_time = time.time() - start_time
            try:
                message = self.receive_queue.get(block=False)
            except queue.Empty:
                pass

        return message

    def stop(self):
        self.connection_status.terminate_early = True
        self.session_thread.join()

    def stop_premature(self):
        self.connection_status.terminate_early = True
        self.send_queue.put(MessageDefinitions.StopSession())
        self.session_thread.join(timeout=2)
