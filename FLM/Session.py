import logging
import queue
import time

from FLM import Channels
from FLM import MessageDefinitions


class BaseSessionManager:
    """Abstract class to manage sending/receiving messages using FLM.
    Start the session, use send and receive functions to get messages synchronously and stop"""
    run = False
    channel = None
    send_queue = queue.Queue()
    receive_queue = queue.Queue()
    channel_receive_queue = queue.Queue()

    def start(self):
        """Begin sending and receiving messages"""
        self.channel.start_async_receive()

        while self.run:
            time.sleep(0.2)
            self.send_next_message()
            self.receive_next_message()
            if self.channel.connection is None:
                self.stop()

    def stop(self):
        self.run = False
        self.channel.disconnect()

    def send_next_message(self):
        """Check the queue and send a message if one exists"""
        try:
            next_message = self.send_queue.get(block=False)
        except queue.Empty:
            return

        next_message.time_sent = time.time()
        self.channel.send(next_message)
        if next_message.id == MessageDefinitions.StopSession.id:
            self.stop()

    def receive_next_message(self):
        """Check the queue and pass on message if one exists"""
        try:
            next_message = self.channel_receive_queue.get(block=False)
        except queue.Empty:
            return
        except OSError:
            self.stop()
            return

        if next_message.id == MessageDefinitions.StopSession.id:
            self.stop()
            return

        self.receive_queue.put(next_message)


class ClientSessionManager(BaseSessionManager):
    def __init__(self, message_send_queue, message_receive_queue, l_port, r_ip, r_port):
        self.channel_receive_queue = queue.Queue()
        self.channel = Channels.ChannelToServer(l_port)
        self.channel.set_async_queue(self.channel_receive_queue)

        self.remote_ip = r_ip
        self.remote_port = r_port
        self.send_queue = message_send_queue
        self.receive_queue = message_receive_queue

    def start(self, cancel_callback):
        self.run = True
        success = self.channel.establish_connection(self.remote_ip, self.remote_port)
        if not success:
            cancel_callback()
            logging.warning("Could not establish connection to server.")
            return False
        super().start()


class ServerSessionManager(BaseSessionManager):
    def __init__(self, message_send_queue, message_receive_queue, local_socket):
        self.channel_receive_queue = queue.Queue()
        self.channel = Channels.ChannelToClient(local_socket)
        self.channel.set_async_queue(self.channel_receive_queue)

        self.send_queue = message_send_queue
        self.receive_queue = message_receive_queue

    def start(self, connection_communicator=None):
        self.run = True
        self.channel.establish_connection(connection_communicator)
        if not connection_communicator.success:
            return False
        super().start()
