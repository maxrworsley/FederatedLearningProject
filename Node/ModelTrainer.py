import ClientTensorflowHandler
import DataWrapper
from FLM import MessageDefinitions


class ModelTrainer:
    def train(self, message, filepath):
        if message.id != MessageDefinitions.RequestTrainModel.id:
            return False

        data_wrapper = DataWrapper.DataWrapper(filepath)
        tf_handler = ClientTensorflowHandler.TensorflowHandler("Client_TF_Handler", data_wrapper)
        tf_handler.get_data()
        tf_handler.create_model()
        tf_handler.fit_model(20)
