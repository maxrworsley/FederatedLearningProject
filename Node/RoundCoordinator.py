from FLM import MessageDefinitions
from FLM import Session
from ModelTrainer import ModelTrainer

import threading
import queue


class RoundCoordinator:
    send_q = None
    receive_q = None
    configuration_manager = None
    client_session = None
    client_thread = None

    def __init__(self, config_manager):
        self.configuration_manager = config_manager

    def start_round(self):
        self.send_q, self.receive_q = queue.Queue(), queue.Queue()
        self.client_session = Session.ClientSessionManager(self.send_q, self.receive_q, 40401, "172.17.0.1", 40400)
        self.client_thread = threading.Thread(target=self.client_session.start)
        self.client_thread.start()

        success = self.train()
        self.stop_round(success)

    def stop_round(self, round_success):
        if round_success:
            print("Completed training successfully. Disconnecting")
        else:
            print("Training did not complete successfully")

        self.send_q.put(MessageDefinitions.StopSession(0, 0, 0, 0))
        self.client_thread.join()

    def train(self):
        model_trainer = ModelTrainer()

        message = self.receive_q.get(block=True)
        model_trainer.train(message, self.configuration_manager.file_path)
        self.send_q.put(MessageDefinitions.ResponseJoinRound(0, 0, 0, 0))
        return True
