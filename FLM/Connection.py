from socket import *


class Connection:
    PACKET_LENGTH_BYTES = 4
    connection = None
    remote_address = None
    socket = None

    def __init__(self, local_ip="", local_port=40400, is_server=False):
        self.ip = local_ip
        self.port = local_port
        self.is_server = is_server

    def set_defaults(self):
        self.connection = None
        self.remote_address = None
        self.socket = None

    def connect_to_remote(self, remote_ip, remote_port):
        if self.is_server:
            return False

        self.disconnect()
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        try:
            self.socket.bind((self.ip, self.port))
            self.socket.connect((remote_ip, remote_port))
        except ConnectionRefusedError:
            return False

        return True

    def wait_for_connection(self):
        if not self.is_server:
            return False

        self.disconnect()
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.socket.bind((self.ip, self.port))
        self.socket.listen(1)
        self.connection, self.remote_address = self.socket.accept()

        return True

    def disconnect(self):
        if self.connection:
            self.connection.close()
        if self.socket:
            self.socket.close()

        self.set_defaults()

    def send_bytes(self, message_bytes):
        packet_length = len(message_bytes).to_bytes(self.PACKET_LENGTH_BYTES, byteorder='big')
        packet = bytearray(packet_length + message_bytes)

        try:
            if self.is_server:
                self.connection.sendall(packet)
            else:
                self.socket.sendall(packet)
        except ConnectionError:
            self.disconnect()
            return False

        return True

    def receive_bytes(self):
        if self.is_server:
            bytes_received = self.get_full_packet(self.connection)
        else:
            bytes_received = self.get_full_packet(self.socket)

        return bytes_received

    def get_full_packet(self, receiving_socket, buffer_size=2048):
        packet_length_bytes = receiving_socket.recv(self.PACKET_LENGTH_BYTES)
        packet_length = int.from_bytes(packet_length_bytes, byteorder='big')

        data = bytearray()
        while packet_length > 0:
            new_data = receiving_socket.recv(min(buffer_size, packet_length))
            data += new_data
            packet_length -= len(new_data)

        return data
