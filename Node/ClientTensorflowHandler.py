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
    location = None

    def get_model_bytes_remove_directory(self, config):
        """
        Save the current model, create a checkpoint of it, get the bytes and remove the checkpoint
        :param config: Contains the working directory to save the model in and delete
        :return: The model checkpoint zipped as bytes
        """
        working_path = config.working_directory

        self.model_trainer.save_model(working_path)
        self.checkpoint_handler.create_checkpoint()
        return self.checkpoint_handler.get_saved_checkpoint_bytes()

    def train(self, config):
        """
        Save and load the model in the working directory. Then perform training as per message instructions
        :param config: Contains the working directory to use for the model
        :return:
        """
        self.checkpoint_handler = CheckpointHandler(config.working_directory)
        data_wrapper = DataWrapper.DataWrapper(config.file_path)
        self.model_trainer = ModelTrainer(data_wrapper)
        self.model_trainer.get_data()
        self.location = data_wrapper.location

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
