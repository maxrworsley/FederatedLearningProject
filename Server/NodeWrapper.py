from FLM import Session
from FLM import MessageDefinitions
import queue
import threading


class NodeWrapper:
    send_queue = None
    receive_queue = None
    server_session = None
    session_thread = None

    def __init__(self, local_socket):
        self.send_queue, self.receive_queue = queue.Queue(), queue.Queue()
        self.server_session = Session.ServerSessionManager(self.send_queue, self.receive_queue, local_socket)

    def start(self):
        self.session_thread = threading.Thread(target=self.server_session.start)
        self.session_thread.start()

    def send(self, message):
        self.send_queue.put(message)

    def receive(self, block=False):
        return self.receive_queue.get(block=block)

    def stop(self):
        self.session_thread.join()

    def stop_premature(self):
        self.send_queue.put(MessageDefinitions.StopSession())
