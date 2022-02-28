import DataWrapper
from ModelTrainer import ModelTrainer


class TensorflowHandler:
    received_bytes = None

    def train(self, filepath):
        data_wrapper = DataWrapper.DataWrapper(filepath)
        model_trainer = ModelTrainer(data_wrapper)
        model_trainer.get_data()
        model_trainer.create_model()
        model_trainer.fit_model(20)
