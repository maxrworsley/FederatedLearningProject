from FLM import MessageDefinitions
from FLM import Session
import ClientTensorflowHandler
import DataWrapper

import threading
import queue


class RoundCoordinator:
    send_q = None
    receive_q = None
    configuration_manager = None

    def __init__(self, config_manager):
        self.configuration_manager = config_manager

    def start_round(self):
        self.send_q, self.receive_q = queue.Queue(), queue.Queue()
        client_session = Session.ClientSessionManager(self.send_q, self.receive_q, 40401, "172.17.0.1", 40400)
        client_thread = threading.Thread(target=client_session.start)
        client_thread.start()

        success = self.train()

        if success:
            print("Completed training successfully. Disconnecting")
        else:
            print("Training did not complete successfully")

        self.send_q.put(MessageDefinitions.StopSession(0, 0, 0, 0))
        client_thread.join()

    def train(self):
        message = self.receive_q.get(block=True)
        if message.id != MessageDefinitions.RequestTrainModel.id:
            return False

        data_wrapper = DataWrapper.DataWrapper(self.configuration_manager.file_path)
        tf_handler = ClientTensorflowHandler.TensorflowHandler("Client_TF_Handler", data_wrapper)
        tf_handler.get_data()
        tf_handler.create_model()
        tf_handler.fit_model(20)

        self.send_q.put(MessageDefinitions.ResponseJoinRound(0, 0, 0, 0))
        return True
