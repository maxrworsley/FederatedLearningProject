import Connection
import Serialisation


class BaseChannel:
    connection = None

    def establish_connection(self, target_ip, target_port):
        pass

    def disconnect(self):
        self.connection.disconnect()

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


class ChannelToServer(BaseChannel):
    def __init__(self, local_port):
        self.connection = Connection.Connection(local_port=local_port, is_server=False)

    def establish_connection(self, target_ip, target_port):
        super().establish_connection(target_ip, target_port)
        self.connection.connect_to_remote(target_ip, target_port)


class ChannelToClient(BaseChannel):
    def __init__(self, local_port, local_ip):
        self.connection = Connection.Connection(local_ip=local_ip, local_port=local_port, is_server=True)

    def establish_connection(self, target_ip, target_port):
        super().establish_connection(target_ip, target_port)
        self.connection.wait_for_connection()
