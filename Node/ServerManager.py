import queue
import threading

from FLM import MessageDefinitions
from FLM import Session


class ServerManager:
    """Wraps the communication with the server"""
    client_session = None
    client_thread = None
    send_queue = None
    receive_queue = None
    config = None
    round_id = -1
    sender_id = -1
    receiver_id = -1

    def __init__(self, configuration):
        self.send_queue = queue.Queue()
        self.receive_queue = queue.Queue()
        self.config = configuration

    def start(self, cancel_callback):
        self.client_session = Session.ClientSessionManager(self.send_queue, self.receive_queue,
                                                           self.config.local_port,
                                                           self.config.remote_ip, self.config.remote_port)
        self.client_thread = threading.Thread(target=self.client_session.start, args=(cancel_callback, ))
        self.client_thread.start()

    def send_message(self, message):
        # Add attributes to message before sending
        message.round_id = self.round_id
        message.sender_id = self.sender_id
        message.receiver_id = self.receiver_id

        self.send_queue.put(message)

    def get_next_message(self):
        try:
            new_message = self.receive_queue.get(block=False)
        except queue.Empty:
            return None

        if new_message.id == MessageDefinitions.ResponseJoinRound.id:
            if new_message.accepted_into_round:
                self.sender_id = new_message.receiver_id
                self.receiver_id = new_message.sender_id
                self.round_id = new_message.round_id

        return new_message

    def stop(self):
        self.send_message(MessageDefinitions.StopSession())
        self.client_thread.join()
