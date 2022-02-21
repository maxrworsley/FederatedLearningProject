import queue
import threading
from sys import argv

from FLM import Session
from FLM import MessageDefinitions
import ClientTensorflowHandler
import DataWrapper


def setup(send_queue, receive_queue):
    client_session = Session.ClientSessionManager(send_queue, receive_queue, 40401, "172.17.0.1", 40400)
    client_thread = threading.Thread(target=client_session.start)
    client_thread.start()
    return client_session, client_thread


def do_training(data_filepath, send_q, receive_q):
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


def start(filepath):
    send_queue, receive_queue = queue.Queue(), queue.Queue()
    client_session, client_thread = setup(send_queue, receive_queue)
    success = do_training(filepath, send_queue, receive_queue)

    if success:
        print("Completed training successfully. Disconnecting")
    else:
        print("Training did not complete successfully")

    send_queue.put(MessageDefinitions.StopSession(0, 0, 0, 0))
    client_thread.join()


if __name__ == '__main__':
    run_on_desktop = False
    file_path = "/home/FLS/Node/data.csv"
    if len(argv) > 1:
        if argv[1] == "-d" or argv[1] == "-D":
            run_on_desktop = True
            file_path = "/home/max/Documents/FederatedLearning/FederatedLearningProject/Node/data.csv"
    print(f"Running tensorflow and FLM with run_on_desktop set to {run_on_desktop}")
    start(file_path)
