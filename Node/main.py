import queue

from FLM import Session

if __name__ == '__main__':
    print("Running with FLM import")
    send_queue, receive_queue = queue.Queue(), queue.Queue()
    client_session = Session.ClientSessionManager(send_queue, receive_queue, 40401, "127.0.0.1", 40400)
