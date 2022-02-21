from FLM import Session
from FLM import MessageDefinitions
import ClientTensorflowHandler
import DataWrapper

import queue
import threading


class Node:
    def setup(self, send_queue, receive_queue):
        client_session = Session.ClientSessionManager(send_queue, receive_queue, 40401, "172.17.0.1", 40400)
        client_thread = threading.Thread(target=client_session.start)
        client_thread.start()
        return client_session, client_thread

    def do_training(self, data_filepath, send_q, receive_q):
        message = receive_q.get(block=True)
        if message.id != MessageDefinitions.RequestTrainModel.id:
            return False

        data_wrapper = DataWrapper.DataWrapper(data_filepath)
        tf_handler = ClientTensorflowHandler.TensorflowHandler("Client_TF_Handler", data_wrapper)
        tf_handler.get_data()
        tf_handler.create_model()
        tf_handler.fit_model(20)

        send_q.put(MessageDefinitions.ResponseJoinRound(0, 0, 0, 0))
        return True

    def start(self, config_manager):
        send_queue, receive_queue = queue.Queue(), queue.Queue()
        client_session, client_thread = self.setup(send_queue, receive_queue)
        success = self.do_training(config_manager.file_path, send_queue, receive_queue)

        if success:
            print("Completed training successfully. Disconnecting")
        else:
            print("Training did not complete successfully")

        send_queue.put(MessageDefinitions.StopSession(0, 0, 0, 0))
        client_thread.join()
