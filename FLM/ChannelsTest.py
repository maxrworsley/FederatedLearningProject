import unittest
import Channels
import Connection
import MessageDefinitions
import threading


class ChannelUsage(unittest.TestCase):
    def test_connection(self):
        server_port = 40400
        new_socket = Connection.get_new_server_socket("", server_port)
        client_channel_to_server, server_channel_to_client = self.make_client_server_channels(new_socket, server_port)

        self.connect_client_server(server_channel_to_client, client_channel_to_server, 40400)

        self.assertTrue(client_channel_to_server.connection is not None)
        client_channel_to_server.disconnect()
        self.assertTrue(client_channel_to_server.connection is None)

        new_socket.close()

    def test_send_message_to_server(self):
        server_port = 40400
        new_socket = Connection.get_new_server_socket("", server_port)
        client_channel_to_server, server_channel_to_client = self.make_client_server_channels(new_socket, server_port)

        self.connect_client_server(server_channel_to_client, client_channel_to_server, 40400)

        sent_message = MessageDefinitions.BaseMessage(1, 1, 0, 12000)
        client_channel_to_server.send(sent_message)
        received_message = server_channel_to_client.sync_receive()

        self.assertTrue(sent_message.__repr__() == received_message.__repr__())
        new_socket.close()

    @staticmethod
    def connect_client_server(server_channel_to_client, client_channel_to_serer, server_port):
        try:
            server_thread = threading.Thread(target=server_channel_to_client.establish_connection)
            server_thread.start()
            client_thread = threading.Thread(target=client_channel_to_serer.establish_connection,
                                             args=("127.0.0.1", server_port))
            client_thread.start()

            client_thread.join()
            server_thread.join()
        except Exception as e:
            server_channel_to_client.disconnect()
            client_channel_to_serer.disconnect()
            raise e

    @staticmethod
    def make_client_server_channels(server_socket, server_port):
        client_channel_to_server = Channels.ChannelToServer(server_port + 1)
        server_channel_to_client = Channels.ChannelToClient(server_socket)

        return client_channel_to_server, server_channel_to_client


if __name__ == '__main__':
    unittest.main()
