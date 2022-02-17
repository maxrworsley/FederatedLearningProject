import socket
import threading

from FLM import Connection
from FLM import MessageDefinitions
from FLM import Serialisation


class BaseChannel:
    connection = None
    message_queue = None
    async_thread = None
    async_receive = False

    def disconnect(self):
        self.stop_async_receive()
        if self.connection:
            self.connection.disconnect()
            self.connection = None

    def set_async_queue(self, queue):
        self.message_queue = queue

    def send(self, message):
        serialised_message = Serialisation.Serialiser.serialise_message(message)
        self.connection.send_bytes(serialised_message)

    def start_async_receive(self):
        self.stop_async_receive()
        self.async_receive = True
        self.async_thread = threading.Thread(target=self.async_receiver)
        self.async_thread.start()

    def stop_async_receive(self):
        self.async_receive = False

    def async_receiver(self):
        while self.async_receive:
            message = self.receive(False)
            if self.async_receive:
                if message is not None:
                    self.message_queue.put(message)

    def sync_receive(self):
        return self.receive(True)

    def receive(self, synchronous):
        if synchronous:
            message_bytes = None

            while message_bytes is None:
                try:
                    message_bytes = self.connection.receive_bytes()
                except socket.timeout:
                    pass
                except OSError:
                    self.disconnect()
                    return None
        else:
            try:
                message_bytes = self.connection.receive_bytes()
            except socket.timeout:
                return None
            except OSError:
                end_message = MessageDefinitions.StopSession(0, 0, 0, 0)
                self.message_queue.put(end_message)
                self.disconnect()
                return None

        if message_bytes is None:
            return None

        try:
            deserialised_message = Serialisation.Serialiser.deserialise_message(message_bytes)
        except ValueError:
            self.disconnect()
            return None

        return deserialised_message

    def __del__(self):
        if self.connection is not None:
            self.stop_async_receive()
            self.connection.disconnect()


class ChannelToServer(BaseChannel):
    def __init__(self, local_port):
        self.connection = Connection.ConnectionToServer("", local_port)

    def establish_connection(self, target_ip, target_port):
        return self.connection.connect_to_remote(target_ip, target_port)


class ChannelToClient(BaseChannel):
    def __init__(self, local_socket):
        self.connection = Connection.ConnectionToClient(local_socket)

    def establish_connection(self):
        return self.connection.wait_for_connection()
