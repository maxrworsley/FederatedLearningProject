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
        c_send_queue, c_receive_queue = queue.Queue(), queue.Queue()
        s_send_queue, s_receive_queue = queue.Queue(), queue.Queue()
        s_sock_num = 40402
        new_socket = Connection.get_new_server_socket("", s_sock_num)
        client_session = Session.ClientSessionManager(c_send_queue, c_receive_queue, s_sock_num + 1, "127.0.0.1", s_sock_num)
        server_session = Session.ServerSessionManager(s_send_queue, s_receive_queue, new_socket)

        client_thread = threading.Thread(target=client_session.start)
        server_thread = threading.Thread(target=server_session.start)
        server_thread.start()
        client_thread.start()

        c_send_queue.put(MessageDefinitions.BaseMessage(0, 0, 1, 0))
        self.get_message_from_session(s_receive_queue)
        s_send_queue.put(MessageDefinitions.BaseMessage(0, 1, 0, 1))
        self.get_message_from_session(c_receive_queue)

        c_send_queue.put(MessageDefinitions.StopSession(0, 0, 0, 0))
        client_thread.join()
        server_thread.join()
        self.assertTrue(True)
        new_socket.close()

    @staticmethod
    def get_message_from_session(receiving_queue):
        message = None
        while message is None:
            try:
                message = receiving_queue.get(block=False)
            except _queue.Empty:
                pass

        print(message)

if __name__ == '__main__':
    unittest.main()
