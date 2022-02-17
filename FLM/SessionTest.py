import _queue
import queue
import threading
import unittest

import Connection
import MessageDefinitions
import Session


class SessionManagerTests(unittest.TestCase):
    def test_session_connection(self):
        s_sock_num = 40400
        c_send_queue, c_receive_queue = queue.Queue(), queue.Queue()
        s_send_queue, s_receive_queue = queue.Queue(), queue.Queue()
        new_socket = Connection.get_new_server_socket("", s_sock_num)
        client_session = Session.ClientSessionManager(c_send_queue, c_receive_queue, s_sock_num + 1, "127.0.0.1",
                                                      s_sock_num)
        server_session = Session.ServerSessionManager(s_send_queue, s_receive_queue, new_socket)

        client_thread = threading.Thread(target=client_session.start)
        server_thread = threading.Thread(target=server_session.start)
        server_thread.start()
        client_thread.start()

        c_send_queue.put(MessageDefinitions.StopSession(0, 0, 0, 0))
        client_thread.join()
        server_thread.join()
        self.assertTrue(True)
        new_socket.close()

    def test_session_send(self):
        s_sock_num = 40402
        c_send_queue, c_receive_queue = queue.Queue(), queue.Queue()
        s_send_queue, s_receive_queue = queue.Queue(), queue.Queue()
        new_socket = Connection.get_new_server_socket("", s_sock_num)
        client_session = Session.ClientSessionManager(c_send_queue, c_receive_queue,
                                                      s_sock_num + 1, "127.0.0.1", s_sock_num)
        server_session = Session.ServerSessionManager(s_send_queue, s_receive_queue, new_socket)

        client_thread = threading.Thread(target=client_session.start)
        server_thread = threading.Thread(target=server_session.start)
        server_thread.start()
        client_thread.start()

        first_message_sent = MessageDefinitions.BaseMessage(0, 0, 1, 0)
        c_send_queue.put(first_message_sent)
        first_message_received = self.get_message_from_session(s_receive_queue)
        second_message_sent = MessageDefinitions.BaseMessage(0, 1, 0, 1)
        s_send_queue.put(second_message_sent)
        second_message_received = self.get_message_from_session(c_receive_queue)

        c_send_queue.put(MessageDefinitions.StopSession(0, 0, 0, 0))
        client_thread.join(timeout=3)
        server_thread.join(timeout=3)
        self.assertTrue(first_message_sent.__repr__() == first_message_received.__repr__())
        self.assertTrue(second_message_sent.__repr__() == second_message_received.__repr__())
        new_socket.close()

    def test_multiple_clients(self):
        s_sock_num = 40404
        c1_send_queue, c1_receive_queue = queue.Queue(), queue.Queue()
        c2_send_queue, c2_receive_queue = queue.Queue(), queue.Queue()
        s1_send_queue, s1_receive_queue = queue.Queue(), queue.Queue()
        s2_send_queue, s2_receive_queue = queue.Queue(), queue.Queue()
        new_socket = Connection.get_new_server_socket("", s_sock_num)
        client_session_1 = Session.ClientSessionManager(c1_send_queue, c1_receive_queue, s_sock_num + 1, "127.0.0.1",
                                                        s_sock_num)
        client_session_2 = Session.ClientSessionManager(c2_send_queue, c2_receive_queue, s_sock_num + 2, "127.0.0.1",
                                                        s_sock_num)
        server_session_1 = Session.ServerSessionManager(s1_send_queue, s1_receive_queue, new_socket)
        server_session_2 = Session.ServerSessionManager(s2_send_queue, s2_receive_queue, new_socket)

        client1_thread = threading.Thread(target=client_session_1.start)
        client2_thread = threading.Thread(target=client_session_2.start)
        server1_thread = threading.Thread(target=server_session_1.start)
        server2_thread = threading.Thread(target=server_session_2.start)
        server1_thread.start()
        server2_thread.start()
        client1_thread.start()
        client2_thread.start()

        # c1_send_queue.put(MessageDefinitions.BaseMessage(0, 1, 0, 0))
        # c1_send_queue.put(MessageDefinitions.BaseMessage(0, 1, 0, 1))
        # c2_send_queue.put(MessageDefinitions.BaseMessage(0, 2, 0, 2))
        # c2_send_queue.put(MessageDefinitions.BaseMessage(0, 2, 0, 3))

        s1_send_queue.put(MessageDefinitions.StopSession(0, 0, 0, 0))
        s2_send_queue.put(MessageDefinitions.StopSession(0, 0, 0, 0))

        client1_thread.join(timeout=3)
        client2_thread.join(timeout=3)
        server1_thread.join(timeout=3)
        server2_thread.join(timeout=3)

        self.assertFalse(client1_thread.is_alive())
        self.assertFalse(client2_thread.is_alive())
        self.assertFalse(server1_thread.is_alive())
        self.assertFalse(server2_thread.is_alive())
        new_socket.close()

    @staticmethod
    def get_message_from_session(receiving_queue):
        message = None
        while message is None:
            try:
                message = receiving_queue.get(block=False)
            except _queue.Empty:
                pass

        return message


if __name__ == '__main__':
    unittest.main()
