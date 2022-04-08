import os
import shutil
from pathlib import Path


class CheckpointHandler:
    """Create, unpack and get bytes for a checkpoint. A checkpoint is a zipped model"""
    def __init__(self, working_directory, remove_directory=True):
        self.checkpoint_directory = working_directory
        self.checkpoint_file_path = working_directory + "/model_checkpoint.zip"
        self.remove_directory = remove_directory
        Path(working_directory).mkdir(parents=True, exist_ok=True)

    def get_checkpoint_path(self):
        return self.checkpoint_file_path

    def create_checkpoint(self):
        owd = os.getcwd()
        try:
            os.chdir(self.checkpoint_directory)
            shutil.make_archive("model_checkpoint", "zip", "./model")
        finally:
            os.chdir(owd)

    def save_unpack_checkpoint(self, checkpoint_bytes):
        with open(self.checkpoint_file_path, mode='wb') as newFile:
            newFile.write(checkpoint_bytes)

        owd = os.getcwd()

        try:
            os.chdir(self.checkpoint_directory)
            shutil.unpack_archive("model_checkpoint.zip", "./model")
        finally:
            os.chdir(owd)

    def get_saved_checkpoint_bytes(self):
        with open(self.checkpoint_file_path, "rb") as read_file:
            return read_file.read()

    def __del__(self):
        try:
            if self.remove_directory:
                shutil.rmtree(self.checkpoint_directory)
        except OSError as e:
            # Could not delete directory as didn't exist
            pass
