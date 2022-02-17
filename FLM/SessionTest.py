import _queue
import time

import MessageDefinitions
import unittest
import Session
import queue
import Connection
import threading


class SessionManagerTests(unittest.TestCase):
    def test_session_connection(self):
        s_sock_num = 40400
        c_send_queue, c_receive_queue = queue.Queue(), queue.Queue()
        s_send_queue, s_receive_queue = queue.Queue(), queue.Queue()
        new_socket = Connection.get_new_server_socket("", s_sock_num)
        client_session = Session.ClientSessionManager(c_send_queue, c_receive_queue, s_sock_num + 1, "127.0.0.1", s_sock_num)
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
        client_thread.join()
        server_thread.join()
        self.assertTrue(first_message_sent.__repr__() == first_message_received.__repr__())
        self.assertTrue(second_message_sent.__repr__() == second_message_received.__repr__())
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
