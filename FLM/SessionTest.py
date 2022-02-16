import _queue

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
        client_thread.start()
        server_thread.start()

        c_send_queue.put(MessageDefinitions.BaseMessage(0, 0, 0, 0))
        message = None
        while message is None:
            try:
                message = s_receive_queue.get()
            except _queue.Empty:
                pass
        print(message)
        # c_send_queue.put(MessageDefinitions.StopSession(0, 0, 0, 0))
        client_thread.join()
        server_thread.join()
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
