import threading

from FLM import MessageDefinitions
from FLM import Session


class ServerManager:
    client_session = None
    client_thread = None
    send_queue = None
    receive_queue = None

    def __init__(self, send_queue, receive_queue):
        self.send_queue = send_queue
        self.receive_queue = receive_queue

    def start(self):
        self.client_session = Session.ClientSessionManager(self.send_queue, self.receive_queue, 40401, "172.17.0.1", 40400)
        self.client_thread = threading.Thread(target=self.client_session.start)
        self.client_thread.start()

    def stop(self):
        self.send_queue.put(MessageDefinitions.StopSession(0, 0, 0, 0))
        self.client_thread.join()
