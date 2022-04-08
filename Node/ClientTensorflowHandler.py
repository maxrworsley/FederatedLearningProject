import DataWrapper
from FLM.CheckpointHandler import CheckpointHandler
from ModelTrainer import ModelTrainer, StopTrainingCallback


class TensorflowHandler:
    """Handles all model training for the client"""
    received_bytes = None
    training_epochs = None
    validation_split = None
    keep_training = True
    stopping_callback = None
    training_thread = None
    model_trainer = None
    checkpoint_handler = None

    def get_model_bytes_remove_directory(self, config):
        working_path = config.working_directory

        self.model_trainer.save_model(working_path)
        self.checkpoint_handler.create_checkpoint()
        return self.checkpoint_handler.get_saved_checkpoint_bytes()

    def train(self, config):
        self.checkpoint_handler = CheckpointHandler(config.working_directory)
        data_wrapper = DataWrapper.DataWrapper(config.file_path)
        self.model_trainer = ModelTrainer(data_wrapper)
        self.model_trainer.get_data()

        if self.received_bytes:
            self.checkpoint_handler.save_unpack_checkpoint(self.received_bytes)
            self.model_trainer.load_model(config.working_directory)
        else:
            self.model_trainer.create_model()

        self.stopping_callback = StopTrainingCallback()
        self.model_trainer.fit_model(self.training_epochs, self.validation_split, self.stopping_callback)

    def get_most_recent_history(self):
        return self.model_trainer.history[-1]

    def stop_training(self):
        if self.stopping_callback:
            self.stopping_callback.keep_training = False
