import _queue
import queue
import Channels
import time
from FLM import MessageDefinitions


class BaseSessionManager:
    run = False
    channel = None
    send_queue = queue.Queue()
    receive_queue = queue.Queue()
    channel_receive_queue = queue.Queue()

    def start(self):
        self.channel.start_async_receive()

        while self.run:
            time.sleep(0.5)
            self.send_next_message()
            self.receive_next_message()
            if self.channel.connection is None:
                self.stop()

    def stop(self):
        self.run = False
        self.channel.disconnect()

    def send_next_message(self):
        try:
            next_message = self.send_queue.get(block=False)
        except _queue.Empty:
            return

        if next_message.id == MessageDefinitions.StopSession.id:
            self.stop()
        else:
            self.channel.send(next_message)

    def receive_next_message(self):
        try:
            next_message = self.channel_receive_queue.get(block=False)
        except _queue.Empty:
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

    def start(self):
        self.run = True
        success = self.channel.establish_connection(self.remote_ip, self.remote_port)
        if not success:
            print("Could not establish connection to server. Stopping.")
            return False
        super().start()


class ServerSessionManager(BaseSessionManager):
    def __init__(self, message_send_queue, message_receive_queue, local_socket):
        self.channel_receive_queue = queue.Queue()
        self.channel = Channels.ChannelToClient(local_socket)
        self.channel.set_async_queue(self.channel_receive_queue)

        self.send_queue = message_send_queue
        self.receive_queue = message_receive_queue

    def start(self):
        self.run = True
        success = self.channel.establish_connection()
        if not success:
            print("Could not establish connection to client. Stopping.")
            return False
        super().start()
