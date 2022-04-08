import socket
import time
from socket import *


def get_new_server_socket(ip, port):
    """Used to set correct parameters for a server socket"""
    new_socket = socket(AF_INET, SOCK_STREAM)
    # Allow reuse of socket immediately after closing
    new_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    # Timeout for connections
    new_socket.settimeout(0.5)
    new_socket.bind((ip, port))
    new_socket.listen(10)
    return new_socket


class Connection:
    """Abstract class to handle packets"""
    PACKET_LENGTH_BYTES = 4
    socket = None

    def get_full_packet(self, receiving_socket, buffer_size=2048):
        try:
            packet_length_bytes = receiving_socket.recv(self.PACKET_LENGTH_BYTES)
        except AttributeError:
            return None
        packet_length = int.from_bytes(packet_length_bytes, byteorder='big')

        data = bytearray()
        while packet_length > 0:
            # Don't receive any more than the remainder of the message
            new_data = receiving_socket.recv(min(buffer_size, packet_length))
            data += new_data
            packet_length -= len(new_data)

        return data


class ConnectionToServer(Connection):
    """Used by channels to manage connection to server"""
    def __init__(self, l_ip, l_port):
        self.ip = l_ip
        self.port = l_port

    def disconnect(self):
        if self.socket is not None:
            self.socket.close()

    def connect_to_remote(self, remote_ip, remote_port):
        self.disconnect()
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.socket.settimeout(0.5)

        try:
            self.socket.connect((remote_ip, remote_port))
        except ConnectionRefusedError:
            return False

        return True

    def send_bytes(self, message_bytes):
        packet_length = len(message_bytes).to_bytes(self.PACKET_LENGTH_BYTES, byteorder='big')
        packet = bytearray(packet_length + message_bytes)

        try:
            self.socket.sendall(packet)
        except ConnectionError:
            self.disconnect()
            return False

        return True

    def receive_bytes(self):
        bytes_received = self.get_full_packet(self.socket)

        return bytes_received


class ConnectionToClient(Connection):
    """Used by channels to manage connection to clients"""
    connection = None
    remote_address = None

    def __init__(self, local_socket):
        self.socket = local_socket

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()

    def send_bytes(self, message_bytes):
        packet_length = len(message_bytes).to_bytes(self.PACKET_LENGTH_BYTES, byteorder='big')
        packet = bytearray(packet_length + message_bytes)

        try:
            self.connection.sendall(packet)
        except ConnectionError:
            self.disconnect()
            return False

        return True

    def receive_bytes(self):
        bytes_received = self.get_full_packet(self.connection)
        return bytes_received

    def wait_for_connection(self, conn_comm):
        self.disconnect()
        for x in range(conn_comm.timeout):
            if conn_comm.terminate_early:
                # Calling function has asked to terminate attempts to connect
                break
            try:
                self.connection, self.remote_address = self.socket.accept()
                if self.connection:
                    conn_comm.success = True
                    return
            except timeout:
                time.sleep(1)

        conn_comm.success = False
        return
