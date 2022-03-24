import DataWrapper
from FLM.CheckpointHandler import CheckpointHandler
from ModelTrainer import ModelTrainer, StopTrainingCallback


class TensorflowHandler:
    received_bytes = None
    training_epochs = None
    validation_split = None
    keep_training = True
    stopping_callback = None
    training_thread = None

    def train(self, config):
        cp_handler = CheckpointHandler(config.working_directory)
        data_wrapper = DataWrapper.DataWrapper(config.file_path)
        model_trainer = ModelTrainer(data_wrapper)
        model_trainer.get_data()

        if self.received_bytes:
            cp_handler.save_unpack_checkpoint(self.received_bytes)
            model_trainer.load_model(config.working_directory)
        else:
            model_trainer.create_model()

        self.stopping_callback = StopTrainingCallback()
        model_trainer.fit_model(self.training_epochs, self.validation_split, self.stopping_callback)

    def stop_training(self):
        if self.stopping_callback:
            self.stopping_callback.keep_training = False
