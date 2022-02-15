import Connection
import Serialisation


class BaseChannel:
    connection = None

    def disconnect(self):
        self.connection.disconnect()
        self.connection = None

    def send(self, message):
        serialised_message = Serialisation.Serialiser.serialise_message(message)
        self.connection.send_bytes(serialised_message)

    def sync_receive(self):
        message_bytes = self.connection.receive_bytes()

        try:
            deserialised_message = Serialisation.Serialiser.deserialise_message(message_bytes)
        except ValueError:
            # todo disconnect?
            return None

        return deserialised_message

    def __del__(self):
        if self.connection is not None:
            self.connection.disconnect()


class ChannelToServer(BaseChannel):
    def __init__(self, local_port):
        self.connection = Connection.ConnectionToServer("", local_port)

    def establish_connection(self, target_ip, target_port):
        self.connection.connect_to_remote(target_ip, target_port)


class ChannelToClient(BaseChannel):
    def __init__(self, local_socket):
        self.connection = Connection.ConnectionToClient(local_socket)

    def establish_connection(self):
        self.connection.wait_for_connection()
